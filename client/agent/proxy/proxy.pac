function FindProxyForURL(url, host) {
  if (shExpMatch(host, "*.api.iclient.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.ifengcloud.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*ifengcloud.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.zhibo.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*zhibo.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.v.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*v.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.v1.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*v1.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*api.iclient.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.dyn.iclient.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*dyn.iclient.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.uc.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*uc.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.pay.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*pay.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.y0.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*y0.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*.y1.ifeng.com")) return "PROXY 127.0.0.1:8888";
  if (shExpMatch(host, "*y1.ifeng.com")) return "PROXY 127.0.0.1:8888";
  return "DIRECT";
}