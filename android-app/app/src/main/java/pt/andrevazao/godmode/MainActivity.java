package pt.andrevazao.godmode;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.DhcpInfo;
import android.net.NetworkInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.text.format.Formatter;
import android.view.ViewGroup;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public class MainActivity extends Activity {
    private static final String PREFS = "god_mode_mobile_prefs";
    private static final String PREF_BASE_URL = "base_url";
    private static final String DEFAULT_BASE_URL = "http://127.0.0.1:8000";
    private static final String ENTRY_ROUTE = "/app/apk-start";
    private static final int HEALTH_TIMEOUT_MS = 1200;

    private WebView webView;
    private EditText baseUrlInput;
    private TextView statusText;
    private TextView routeText;
    private SharedPreferences preferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        preferences = getSharedPreferences(PREFS, MODE_PRIVATE);
        buildUi();
        autoDiscoverAndOpen(true);
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(5, 8, 22));
        root.setLayoutParams(new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
        ));

        statusText = new TextView(this);
        statusText.setTextColor(Color.WHITE);
        statusText.setText("God Mode APK · auto discovery pronto");
        statusText.setPadding(18, 16, 18, 4);
        root.addView(statusText, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        routeText = new TextView(this);
        routeText.setTextColor(Color.LTGRAY);
        routeText.setText("Rota: " + ENTRY_ROUTE);
        routeText.setPadding(18, 0, 18, 8);
        root.addView(routeText, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        controls.setPadding(12, 8, 12, 8);

        baseUrlInput = new EditText(this);
        baseUrlInput.setSingleLine(true);
        baseUrlInput.setText(preferences.getString(PREF_BASE_URL, DEFAULT_BASE_URL));
        baseUrlInput.setTextColor(Color.WHITE);
        baseUrlInput.setHintTextColor(Color.LTGRAY);
        baseUrlInput.setHint("auto ou http://IP_DO_PC:8000");
        baseUrlInput.setBackgroundColor(Color.rgb(15, 23, 42));
        controls.addView(baseUrlInput, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));

        Button openButton = new Button(this);
        openButton.setText("Abrir");
        openButton.setOnClickListener(v -> loadRoute(ENTRY_ROUTE));
        controls.addView(openButton, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));
        root.addView(controls);

        HorizontalScrollView quickScroll = new HorizontalScrollView(this);
        LinearLayout quickButtons = new LinearLayout(this);
        quickButtons.setOrientation(LinearLayout.HORIZONTAL);
        quickButtons.setPadding(12, 0, 12, 8);
        addQuickButton(quickButtons, "Auto", "auto", true, true);
        addQuickButton(quickButtons, "Teste", "/health", true, false);
        addQuickButton(quickButtons, "Start", "/app/apk-start", false, false);
        addQuickButton(quickButtons, "First", "/app/first-use", false, false);
        addQuickButton(quickButtons, "Chat", "/app/operator-chat-sync-cards", false, false);
        addQuickButton(quickButtons, "Readiness", "/app/install-readiness", false, false);
        addQuickButton(quickButtons, "Drill", "/app/e2e-operational-drill", false, false);
        quickScroll.addView(quickButtons);
        root.addView(quickScroll);

        webView = new WebView(this);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                statusText.setText("Aberto · " + url + " · rede: " + networkStatus());
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                statusText.setText("Erro WebView · confirma IP/porta do PC · rede: " + networkStatus());
            }
        });
        webView.setWebChromeClient(new WebChromeClient());
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportZoom(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        webView.setBackgroundColor(Color.rgb(5, 8, 22));
        root.addView(webView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1
        ));

        setContentView(root);
    }

    private void addQuickButton(LinearLayout parent, String label, String route, boolean diagnostic, boolean autoDiscovery) {
        Button button = new Button(this);
        button.setText(label);
        button.setOnClickListener(v -> {
            if (autoDiscovery) {
                autoDiscoverAndOpen(false);
            } else if (diagnostic) {
                testHealth();
            } else {
                loadRoute(route);
            }
        });
        parent.addView(button, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));
    }

    private String normalizeBaseUrl() {
        String baseUrl = baseUrlInput.getText().toString().trim();
        if (baseUrl.isEmpty() || "auto".equalsIgnoreCase(baseUrl)) {
            baseUrl = preferences.getString(PREF_BASE_URL, DEFAULT_BASE_URL);
            baseUrlInput.setText(baseUrl);
        }
        while (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.substring(0, baseUrl.length() - 1);
        }
        preferences.edit().putString(PREF_BASE_URL, baseUrl).apply();
        return baseUrl;
    }

    private void loadRoute(String route) {
        String baseUrl = normalizeBaseUrl();
        String target = route.startsWith("http") ? route : baseUrl + route;
        routeText.setText("Rota: " + route);
        statusText.setText("A abrir: " + target + " · rede: " + networkStatus());
        webView.loadUrl(target);
    }

    private void autoDiscoverAndOpen(boolean silentFallback) {
        statusText.setText("A procurar God Mode no PC... · rede: " + networkStatus());
        routeText.setText("Auto discovery: /health");
        new Thread(() -> {
            List<String> candidates = buildDiscoveryCandidates();
            String found = null;
            int checked = 0;
            for (String candidate : candidates) {
                checked++;
                String finalCandidate = candidate;
                int finalChecked = checked;
                runOnUiThread(() -> statusText.setText("A testar " + finalCandidate + " (" + finalChecked + "/" + candidates.size() + ")"));
                if (isHealthy(candidate, HEALTH_TIMEOUT_MS)) {
                    found = candidate;
                    break;
                }
            }
            String finalFound = found;
            int totalChecked = checked;
            runOnUiThread(() -> {
                if (finalFound != null) {
                    preferences.edit().putString(PREF_BASE_URL, finalFound).apply();
                    baseUrlInput.setText(finalFound);
                    statusText.setText("God Mode encontrado automaticamente: " + finalFound);
                    loadRoute(ENTRY_ROUTE);
                } else {
                    statusText.setText("Não encontrei o PC automaticamente após " + totalChecked + " testes. Escreve o IP do PC ou confirma firewall/porta 8000.");
                    if (silentFallback) {
                        loadRoute(ENTRY_ROUTE);
                    }
                }
            });
        }).start();
    }

    private List<String> buildDiscoveryCandidates() {
        Set<String> candidates = new LinkedHashSet<>();
        addCandidate(candidates, preferences.getString(PREF_BASE_URL, DEFAULT_BASE_URL));
        addCandidate(candidates, DEFAULT_BASE_URL);
        addCandidate(candidates, "http://10.0.2.2:8000");
        addCandidate(candidates, "http://localhost:8000");
        String gateway = gatewayIp();
        if (gateway != null && gateway.contains(".")) {
            addCandidate(candidates, "http://" + gateway + ":8000");
            String prefix = gateway.substring(0, gateway.lastIndexOf('.') + 1);
            int[] likelyHosts = new int[]{1, 2, 10, 20, 50, 100, 101, 102, 150, 200, 254};
            for (int host : likelyHosts) {
                addCandidate(candidates, "http://" + prefix + host + ":8000");
            }
        }
        String phoneIp = phoneIp();
        if (phoneIp != null && phoneIp.contains(".")) {
            String prefix = phoneIp.substring(0, phoneIp.lastIndexOf('.') + 1);
            int[] likelyHosts = new int[]{1, 2, 10, 20, 50, 100, 101, 102, 150, 200, 254};
            for (int host : likelyHosts) {
                addCandidate(candidates, "http://" + prefix + host + ":8000");
            }
        }
        return new ArrayList<>(candidates);
    }

    private void addCandidate(Set<String> candidates, String candidate) {
        if (candidate == null) {
            return;
        }
        String normalized = candidate.trim();
        if (normalized.isEmpty() || "auto".equalsIgnoreCase(normalized)) {
            return;
        }
        while (normalized.endsWith("/")) {
            normalized = normalized.substring(0, normalized.length() - 1);
        }
        if (!normalized.startsWith("http://") && !normalized.startsWith("https://")) {
            normalized = "http://" + normalized;
        }
        candidates.add(normalized);
    }

    private String gatewayIp() {
        try {
            WifiManager wifiManager = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            if (wifiManager == null) {
                return null;
            }
            DhcpInfo dhcpInfo = wifiManager.getDhcpInfo();
            if (dhcpInfo == null || dhcpInfo.gateway == 0) {
                return null;
            }
            return Formatter.formatIpAddress(dhcpInfo.gateway);
        } catch (Exception ignored) {
            return null;
        }
    }

    private String phoneIp() {
        try {
            WifiManager wifiManager = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            if (wifiManager == null || wifiManager.getConnectionInfo() == null) {
                return null;
            }
            int ip = wifiManager.getConnectionInfo().getIpAddress();
            if (ip == 0) {
                return null;
            }
            return Formatter.formatIpAddress(ip);
        } catch (Exception ignored) {
            return null;
        }
    }

    private boolean isHealthy(String baseUrl, int timeoutMs) {
        HttpURLConnection connection = null;
        try {
            URL url = new URL(baseUrl + "/health");
            connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(timeoutMs);
            connection.setReadTimeout(timeoutMs);
            connection.setRequestMethod("GET");
            int code = connection.getResponseCode();
            return code >= 200 && code < 400;
        } catch (Exception ignored) {
            return false;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private void testHealth() {
        String baseUrl = normalizeBaseUrl();
        String target = baseUrl + "/health";
        routeText.setText("Teste: /health");
        statusText.setText("A testar backend: " + target);
        new Thread(() -> {
            String message;
            boolean ok = false;
            HttpURLConnection connection = null;
            try {
                URL url = new URL(target);
                connection = (HttpURLConnection) url.openConnection();
                connection.setConnectTimeout(3500);
                connection.setReadTimeout(3500);
                connection.setRequestMethod("GET");
                int code = connection.getResponseCode();
                BufferedReader reader = new BufferedReader(new InputStreamReader(
                        code >= 200 && code < 400 ? connection.getInputStream() : connection.getErrorStream()
                ));
                StringBuilder body = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    body.append(line);
                    if (body.length() > 120) {
                        break;
                    }
                }
                ok = code >= 200 && code < 400;
                message = (ok ? "Backend OK" : "Backend respondeu erro") + " · HTTP " + code + " · " + body;
            } catch (Exception exc) {
                message = "Falha no teste · tenta Auto ou verifica IP do PC, firewall e se o backend está aberto · " + exc.getClass().getSimpleName();
            } finally {
                if (connection != null) {
                    connection.disconnect();
                }
            }
            boolean finalOk = ok;
            String finalMessage = message;
            runOnUiThread(() -> {
                statusText.setText(finalMessage);
                if (finalOk) {
                    loadRoute(ENTRY_ROUTE);
                }
            });
        }).start();
    }

    private String networkStatus() {
        try {
            ConnectivityManager manager = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
            NetworkInfo info = manager != null ? manager.getActiveNetworkInfo() : null;
            return info != null && info.isConnected() ? "online" : "offline";
        } catch (Exception ignored) {
            return "unknown";
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
            return;
        }
        super.onBackPressed();
    }
}
