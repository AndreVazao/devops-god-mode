package pt.andrevazao.godmode;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.DhcpInfo;
import android.net.NetworkInfo;
import android.net.Uri;
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
    private static final String ENTRY_ROUTE = "/app/home";
    private static final int HEALTH_TIMEOUT_MS = 900;

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
        handleUrlIntent(getIntent());
        autoDiscoverAndOpen(true);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleUrlIntent(intent);
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(5, 8, 22));

        statusText = new TextView(this);
        statusText.setTextColor(Color.WHITE);
        statusText.setText("God Mode APK · a procurar PC");
        statusText.setPadding(18, 16, 18, 4);
        root.addView(statusText);

        routeText = new TextView(this);
        routeText.setTextColor(Color.LTGRAY);
        routeText.setText("Rota principal: " + ENTRY_ROUTE);
        routeText.setPadding(18, 0, 18, 8);
        root.addView(routeText);

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        controls.setPadding(12, 8, 12, 8);

        baseUrlInput = new EditText(this);
        baseUrlInput.setSingleLine(true);
        baseUrlInput.setText(preferences.getString(PREF_BASE_URL, DEFAULT_BASE_URL));
        baseUrlInput.setTextColor(Color.WHITE);
        baseUrlInput.setHintTextColor(Color.LTGRAY);
        baseUrlInput.setHint("http://IP_DO_PC:8000");
        baseUrlInput.setBackgroundColor(Color.rgb(15, 23, 42));
        controls.addView(baseUrlInput, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));

        Button homeButton = new Button(this);
        homeButton.setText("Home");
        homeButton.setOnClickListener(v -> loadRoute(ENTRY_ROUTE));
        controls.addView(homeButton);
        root.addView(controls);

        HorizontalScrollView quickScroll = new HorizontalScrollView(this);
        LinearLayout quickButtons = new LinearLayout(this);
        quickButtons.setOrientation(LinearLayout.HORIZONTAL);
        quickButtons.setPadding(12, 0, 12, 8);
        addQuickButton(quickButtons, "Auto", "auto", true, true);
        addQuickButton(quickButtons, "Home", "/app/home", false, false);
        addQuickButton(quickButtons, "Chat", "/app/operator-chat-sync-cards", false, false);
        addQuickButton(quickButtons, "OK", "/app/mobile-approval-cockpit-v2", false, false);
        addQuickButton(quickButtons, "PC", "/app/pc-autopilot", false, false);
        addQuickButton(quickButtons, "Teste", "/health", true, false);
        quickScroll.addView(quickButtons);
        root.addView(quickScroll);

        webView = new WebView(this);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                statusText.setText("Aberto · " + url + " · " + networkStatus());
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request == null || request.isForMainFrame()) {
                    String path = request != null && request.getUrl() != null ? request.getUrl().getPath() : ENTRY_ROUTE;
                    showOfflineScreen(path);
                }
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
        root.addView(webView, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));

        setContentView(root);
    }

    private void handleUrlIntent(Intent intent) {
        if (intent == null || intent.getData() == null) {
            return;
        }
        Uri uri = intent.getData();
        String baseUrl = uri.getQueryParameter("base_url");
        if (isSafeBaseUrl(baseUrl)) {
            saveBaseUrl(baseUrl);
        }
    }

    private boolean isSafeBaseUrl(String baseUrl) {
        String value = smartNormalizeUrl(baseUrl);
        if (value == null) {
            return false;
        }
        String lowered = value.toLowerCase();
        return (lowered.startsWith("http://") || lowered.startsWith("https://"))
                && !lowered.contains("?")
                && !lowered.contains("=")
                && lowered.length() < 120;
    }

    private String smartNormalizeUrl(String raw) {
        if (raw == null) {
            return null;
        }
        String value = raw.trim();
        if (value.isEmpty()) {
            return value;
        }
        if (!value.startsWith("http://") && !value.startsWith("https://")) {
            value = "http://" + value;
        }
        if (value.startsWith("http://182.168.")) {
            value = "http://192.168." + value.substring("http://182.168.".length());
        }
        if (value.startsWith("https://182.168.")) {
            value = "https://192.168." + value.substring("https://182.168.".length());
        }
        while (value.endsWith("/")) {
            value = value.substring(0, value.length() - 1);
        }
        return value;
    }

    private void saveBaseUrl(String baseUrl) {
        String value = smartNormalizeUrl(baseUrl);
        if (value == null || value.isEmpty()) {
            return;
        }
        preferences.edit().putString(PREF_BASE_URL, value).apply();
        if (baseUrlInput != null) {
            baseUrlInput.setText(value);
        }
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
        parent.addView(button);
    }

    private String normalizeBaseUrl() {
        String baseUrl = baseUrlInput.getText().toString().trim();
        if (baseUrl.isEmpty() || "auto".equalsIgnoreCase(baseUrl)) {
            baseUrl = preferences.getString(PREF_BASE_URL, DEFAULT_BASE_URL);
        }
        baseUrl = smartNormalizeUrl(baseUrl);
        if (baseUrl == null || baseUrl.isEmpty()) {
            baseUrl = DEFAULT_BASE_URL;
        }
        baseUrlInput.setText(baseUrl);
        preferences.edit().putString(PREF_BASE_URL, baseUrl).apply();
        return baseUrl;
    }

    private void loadRoute(String route) {
        String baseUrl = normalizeBaseUrl();
        String target = route.startsWith("http") ? route : baseUrl + route;
        routeText.setText("Rota: " + route);
        statusText.setText("A abrir: " + target + " · " + networkStatus());
        webView.loadUrl(target);
    }

    private void autoDiscoverAndOpen(boolean firstBoot) {
        statusText.setText("A procurar God Mode no PC... · " + networkStatus());
        routeText.setText("Auto discovery: /health → /app/home");
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
            runOnUiThread(() -> {
                if (finalFound != null) {
                    saveBaseUrl(finalFound);
                    statusText.setText("God Mode encontrado: " + finalFound);
                    loadRoute(ENTRY_ROUTE);
                } else {
                    showOfflineScreen(ENTRY_ROUTE);
                }
            });
        }).start();
    }

    private List<String> buildDiscoveryCandidates() {
        Set<String> candidates = new LinkedHashSet<>();
        addCandidate(candidates, baseUrlInput != null ? baseUrlInput.getText().toString() : null);
        addCandidate(candidates, preferences.getString(PREF_BASE_URL, DEFAULT_BASE_URL));
        addCandidate(candidates, DEFAULT_BASE_URL);
        addCandidate(candidates, "http://10.0.2.2:8000");

        String gateway = gatewayIp();
        if (gateway != null && gateway.contains(".")) {
            addCandidate(candidates, "http://" + gateway + ":8000");
            addLanCandidates(candidates, gateway, 20);
        }

        String phoneIp = phoneIp();
        if (phoneIp != null && phoneIp.contains(".")) {
            addLanCandidates(candidates, phoneIp, 20);
        }
        return new ArrayList<>(candidates);
    }

    private void addLanCandidates(Set<String> candidates, String referenceIp, int neighborRadius) {
        int lastDot = referenceIp.lastIndexOf('.');
        if (lastDot < 0) {
            return;
        }
        String prefix = referenceIp.substring(0, lastDot + 1);
        int[] fixedHosts = new int[]{1, 2, 10, 20, 50, 67, 80, 81, 82, 100, 101, 102, 150, 200, 254};
        for (int host : fixedHosts) {
            addCandidate(candidates, "http://" + prefix + host + ":8000");
        }
        int center = parseLastOctet(referenceIp);
        if (center > 0) {
            int start = Math.max(1, center - neighborRadius);
            int end = Math.min(254, center + neighborRadius);
            for (int host = start; host <= end; host++) {
                addCandidate(candidates, "http://" + prefix + host + ":8000");
            }
        }
    }

    private int parseLastOctet(String ip) {
        try {
            int lastDot = ip.lastIndexOf('.');
            if (lastDot < 0) {
                return -1;
            }
            return Integer.parseInt(ip.substring(lastDot + 1));
        } catch (Exception ignored) {
            return -1;
        }
    }

    private void addCandidate(Set<String> candidates, String candidate) {
        String normalized = smartNormalizeUrl(candidate);
        if (normalized == null || normalized.isEmpty() || "auto".equalsIgnoreCase(normalized)) {
            return;
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
        routeText.setText("Teste: /health → /app/home");
        statusText.setText("A testar backend: " + baseUrl);
        new Thread(() -> {
            boolean ok = isHealthy(baseUrl, 3500);
            runOnUiThread(() -> {
                if (ok) {
                    statusText.setText("Backend OK: " + baseUrl);
                    loadRoute(ENTRY_ROUTE);
                } else {
                    statusText.setText("Backend indisponível: " + baseUrl);
                    showOfflineScreen(ENTRY_ROUTE);
                }
            });
        }).start();
    }

    private void showOfflineScreen(String route) {
        String baseUrl = normalizeBaseUrl();
        routeText.setText("Offline · rota: " + route);
        statusText.setText("A aguardar PC/backend · " + networkStatus());
        String html = "<!doctype html><html lang='pt-PT'><head><meta charset='utf-8'>"
                + "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                + "<style>body{margin:0;background:#050816;color:#eef5ff;font-family:Arial,sans-serif;padding:16px}"
                + ".card{border:1px solid #26344f;background:#0f172a;border-radius:20px;padding:16px;margin-bottom:12px}"
                + "h1{font-size:24px;margin:0 0 8px}p{color:#b8c7e6;line-height:1.45}.pill{display:inline-block;background:#082f49;color:#7dd3fc;border-radius:999px;padding:6px 10px;margin:4px 4px 4px 0;font-weight:bold}"
                + ".warn{color:#fde68a}.muted{color:#9fb0d0}</style></head><body>"
                + "<div class='card'><h1>PC ainda não ligado</h1><p>O APK está instalado. O cérebro do God Mode corre no PC. Enquanto o EXE/backend não estiver aberto, o chat real e os botões ficam à espera.</p>"
                + "<span class='pill'>APK OK</span><span class='pill'>A aguardar PC</span><span class='pill'>" + html(networkStatus()) + "</span></div>"
                + "<div class='card'><h1>Quando chegares ao PC</h1><p>1. Abre <b>GodModeDesktop.exe</b>.</p><p>2. No APK, carrega em <b>Auto</b>.</p><p>3. Se não encontrar, escreve em cima: <b>http://IP_DO_PC:8000</b>.</p><p>4. Depois abre <b>Home</b> ou <b>Chat</b>.</p>"
                + "<p class='warn'>Confirma que escreveste 192.168.x.x e não 182.168.x.x. 127.0.0.1 no telemóvel é o próprio telemóvel, não o PC.</p></div>"
                + "<div class='card'><h1>Estado</h1><p class='muted'>Base atual: " + html(baseUrl) + "</p><p class='muted'>Rota pedida: " + html(route) + "</p><p class='muted'>Auto procura também hosts próximos do IP do telemóvel e hosts comuns como .80, .81 e .82.</p></div>"
                + "</body></html>";
        webView.loadDataWithBaseURL("https://godmode.local/offline", html, "text/html", "UTF-8", null);
    }

    private String html(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&#39;");
    }

    private String networkStatus() {
        try {
            ConnectivityManager manager = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
            NetworkInfo info = manager != null ? manager.getActiveNetworkInfo() : null;
            return info != null && info.isConnected() ? "rede online" : "rede offline";
        } catch (Exception ignored) {
            return "rede desconhecida";
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
