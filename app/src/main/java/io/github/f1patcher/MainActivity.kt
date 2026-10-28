package io.github.f1patcher

import android.app.Activity
import android.content.Intent
import android.graphics.Typeface
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.OpenableColumns
import android.view.View
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.view.WindowInsets
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import com.chaquo.python.PyException
import com.chaquo.python.Python
import java.io.File

/**
 * One screen: pick an APK, patch it with f1mobile_patcher.py, save the result.
 * No AndroidX, no layout XML, no dependencies besides Chaquopy.
 */
class MainActivity : Activity() {

    private companion object {
        const val PICK_APK = 1
        const val SAVE_APK = 2
    }

    private val main = Handler(Looper.getMainLooper())
    private var source: Uri? = null
    private var output: File? = null

    private lateinit var status: TextView
    private lateinit var logView: TextView
    private lateinit var scroll: ScrollView
    private lateinit var pickButton: Button
    private lateinit var patchButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(buildUi())
        status.text = "Pick the original F1 Mobile Racing 5.4.11 APK."
        log("Ready. The store version must be uninstalled before installing the result.")
    }

    private fun buildUi(): View {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(24), dp(24), dp(24), dp(16))
        }

        val title = TextView(this).apply {
            text = "F1 APK Patcher"
            textSize = 22f
            setTypeface(typeface, Typeface.BOLD)
            setPadding(0, 0, 0, dp(16))
        }

        status = TextView(this).apply {
            textSize = 15f
            setPadding(0, 0, 0, dp(12))
        }

        pickButton = Button(this).apply {
            text = "1  Pick APK"
            setOnClickListener { pickApk() }
        }

        patchButton = Button(this).apply {
            text = "2  Patch and save"
            isEnabled = false
            setOnClickListener { startPatch() }
        }

        logView = TextView(this).apply {
            textSize = 11f
            typeface = Typeface.MONOSPACE
            setTextIsSelectable(true)
            setPadding(0, dp(8), 0, 0)
        }

        scroll = ScrollView(this).apply {
            addView(logView, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT))
        }

        root.addView(title, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT))
        root.addView(status, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT))
        root.addView(pickButton, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT))
        root.addView(patchButton, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT))
        root.addView(scroll, LinearLayout.LayoutParams(MATCH_PARENT, 0, 1f))

        // targetSdk 35 draws edge-to-edge, so make room for the system bars ourselves.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            root.setOnApplyWindowInsetsListener { view, insets ->
                val bars = insets.getInsets(
                    WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout()
                )
                view.setPadding(
                    dp(24) + bars.left,
                    dp(24) + bars.top,
                    dp(24) + bars.right,
                    dp(16) + bars.bottom
                )
                insets
            }
        }
        return root
    }

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()

    // ------------------------------------------------------------------ pick

    private fun pickApk() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"
        }
        startActivityForResult(intent, PICK_APK)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val uri = data?.data ?: return
        when (requestCode) {
            PICK_APK -> {
                if (resultCode != RESULT_OK) return
                source = uri
                status.text = "Selected: ${displayName(uri)}"
                log("Selected ${displayName(uri)}")
                patchButton.isEnabled = true
            }
            SAVE_APK -> {
                if (resultCode == RESULT_OK) saveTo(uri)
                else log("Save cancelled; output kept at ${output?.absolutePath}")
            }
        }
    }

    private fun displayName(uri: Uri): String {
        runCatching {
            contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)
                ?.use { cursor ->
                    if (cursor.moveToFirst()) return cursor.getString(0)
                }
        }
        return uri.lastPathSegment ?: uri.toString()
    }

    // ----------------------------------------------------------------- patch

    private fun startPatch() {
        val uri = source ?: return
        logView.text = ""
        pickButton.isEnabled = false
        patchButton.isEnabled = false
        status.text = "Working ..."

        Thread {
            val dir = getExternalFilesDir(null) ?: filesDir
            val input = File(dir, "input.apk")
            val result = File(dir, "f1mobile-5.4.11-offline-patched.apk")
            try {
                log("Copying selected APK ...")
                copyUri(uri, input)
                log("Input: ${input.length() / 1048576} MB")
                Python.getInstance().getModule("runner")
                    .callAttr("run", input.absolutePath, result.absolutePath, Progress())
                output = result
                main.post {
                    status.text = "Patched. Choose where to save the APK."
                    askWhereToSave()
                }
            } catch (e: Exception) {
                val message = (e as? PyException)?.message ?: e.message ?: e.toString()
                main.post {
                    status.text = "Failed."
                    log("ERROR: ${message.trim()}")
                }
            } finally {
                input.delete()
                main.post {
                    pickButton.isEnabled = true
                    patchButton.isEnabled = source != null
                }
            }
        }.start()
    }

    private fun copyUri(uri: Uri, destination: File) {
        val total = runCatching {
            contentResolver.openAssetFileDescriptor(uri, "r")?.use { it.length } ?: -1L
        }.getOrDefault(-1L)

        val input = contentResolver.openInputStream(uri)
            ?: throw IllegalStateException("Cannot read the selected file")
        input.use { from ->
            destination.outputStream().use { to ->
                val buffer = ByteArray(1 shl 20)
                var done = 0L
                var step = -1
                while (true) {
                    val count = from.read(buffer)
                    if (count < 0) break
                    to.write(buffer, 0, count)
                    done += count
                    if (total > 0) {
                        val percent = (done * 100 / total).toInt()
                        if (percent / 10 != step) {
                            step = percent / 10
                            log("  copied $percent%")
                        }
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------ save

    private fun askWhereToSave() {
        val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "application/vnd.android.package-archive"
            putExtra(Intent.EXTRA_TITLE, "f1mobile-5.4.11-offline-patched.apk")
        }
        startActivityForResult(intent, SAVE_APK)
    }

    private fun saveTo(uri: Uri) {
        val file = output ?: return
        status.text = "Saving ..."
        Thread {
            try {
                contentResolver.openOutputStream(uri, "wt")?.use { to ->
                    file.inputStream().use { it.copyTo(to, 1 shl 20) }
                } ?: throw IllegalStateException("Cannot write to the selected location")
                log("Saved ${displayName(uri)} (${file.length() / 1048576} MB)")
                file.delete()
                output = null
                main.post { status.text = "Done." }
            } catch (e: Exception) {
                main.post {
                    status.text = "Save failed."
                    log("ERROR: ${e.message}")
                }
            }
        }.start()
    }

    // ------------------------------------------------------------------- log

    /** Handed to Python so progress lines show up while it runs. */
    inner class Progress {
        fun emit(message: String) {
            log(message)
        }
    }

    private fun log(line: String) {
        if (Looper.myLooper() == Looper.getMainLooper()) append(line)
        else main.post { append(line) }
    }

    private fun append(line: String) {
        logView.append(line + "\n")
        scroll.post { scroll.fullScroll(View.FOCUS_DOWN) }
    }
}
