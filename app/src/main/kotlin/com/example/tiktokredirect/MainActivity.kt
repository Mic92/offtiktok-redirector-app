package com.example.tiktokredirect

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.ComponentActivity
import com.example.tiktokredirect.databinding.ActivityMainBinding

class MainActivity : ComponentActivity() {
    private lateinit var binding: ActivityMainBinding
    private val webView: WebView get() = binding.webView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupWebView()
        setupBackNavigation()
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        intent?.let { handleIntent(it) }
    }

    private fun setupWebView() {
        webView.apply {
            webViewClient = WebViewClient()
            webChromeClient = WebChromeClient()
            settings.configureForRedirect()
        }
    }

    private fun setupBackNavigation() {
        onBackPressedDispatcher.addCallback(
            this,
            object : androidx.activity.OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    if (webView.canGoBack()) {
                        webView.goBack()
                    } else {
                        isEnabled = false
                        onBackPressedDispatcher.onBackPressed()
                    }
                }
            },
        )
    }

    private fun handleIntent(intent: Intent) {
        when {
            intent.isViewAction() -> handleTikTokUrl(intent.data)
            else -> showWelcomeMessage()
        }
    }

    private fun handleTikTokUrl(uri: Uri?) {
        uri?.let {
            val redirectedUrl = it.toString().redirectToOffTikTok()
            Toast.makeText(this, "Opening in OffTikTok...", Toast.LENGTH_SHORT).show()
            webView.loadUrl(redirectedUrl)
        }
    }

    private fun showWelcomeMessage() {
        webView.loadData(
            """
            <html>
            <body style='display:flex;align-items:center;justify-content:center;height:100vh;margin:0;font-family:sans-serif;text-align:center;'>
                <div>
                    <h2>TikTok Redirect</h2>
                    <p>Click on any TikTok link to open it here!</p>
                </div>
            </body>
            </html>
            """.trimIndent(),
            "text/html",
            "UTF-8",
        )
    }

    // Extension functions for better readability
    private fun Intent.isViewAction() = action == Intent.ACTION_VIEW && data != null

    private fun String.redirectToOffTikTok(): String =
        runCatching {
            val originalUri = Uri.parse(this)
            val host = originalUri.host ?: return this

            val newHost = TIKTOK_DOMAIN_MAP[host] ?: return this

            originalUri
                .buildUpon()
                .authority(newHost)
                .build()
                .toString()
        }.getOrElse {
            it.printStackTrace()
            this
        }

    private fun WebSettings.configureForRedirect() {
        javaScriptEnabled = true
        domStorageEnabled = true
        loadWithOverviewMode = true
        useWideViewPort = true
        builtInZoomControls = false
        displayZoomControls = false
        setSupportZoom(false)
        defaultTextEncodingName = "utf-8"
    }

    companion object {
        private val TIKTOK_DOMAIN_MAP =
            mapOf(
                "www.tiktok.com" to "www.offtiktok.com",
                "tiktok.com" to "offtiktok.com",
                "vm.tiktok.com" to "vm.offtiktok.com",
                "vt.tiktok.com" to "vt.offtiktok.com",
            )
    }
}
