package com.example.tiktokredirect

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Toast

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleIntent(intent)
        finish() // Close this activity after redirecting
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        intent?.let {
            handleIntent(it)
            finish()
        }
    }

    private fun handleIntent(intent: Intent) {
        when {
            intent.isViewAction() -> redirectTikTokUrl(intent.data)
            intent.isSendAction() -> handleSharedText(intent)
            else -> {
                Toast.makeText(this, "No TikTok URL to redirect", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun redirectTikTokUrl(uri: Uri?) {
        uri?.let {
            val redirectedUrl = it.toString().redirectToOffTikTok()
            openInBrowser(redirectedUrl)
        }
    }

    private fun handleSharedText(intent: Intent) {
        intent.getStringExtra(Intent.EXTRA_TEXT)?.let { sharedText ->
            val url = sharedText.trim()
            if (url.contains("tiktok.com")) {
                val redirectedUrl = url.redirectToOffTikTok()
                openInBrowser(redirectedUrl)
            } else {
                Toast.makeText(this, "Not a TikTok URL", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun openInBrowser(url: String) {
        val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        Toast.makeText(this, "Opening in OffTikTok...", Toast.LENGTH_SHORT).show()
        startActivity(browserIntent)
    }

    private fun Intent.isViewAction() = action == Intent.ACTION_VIEW && data != null

    private fun Intent.isSendAction() = action == Intent.ACTION_SEND && type == "text/plain"

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
