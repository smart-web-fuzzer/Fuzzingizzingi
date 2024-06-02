import json
from urllib.parse import urlparse, parse_qs

import json
from urllib.parse import urlparse, parse_qs

class HTTPRequest:
    def __init__(self, method, url, headers=None, body=None, cookies=None, user_agent=None, protocol_version="HTTP/1.1"):
        self.method = method
        self.url = url
        self.headers = headers if headers is not None else {}
        self.body = body
        self.cookies = cookies if cookies is not None else {}
        self.user_agent = user_agent
        self.protocol_version = protocol_version

        self.url_params = self.parse_url_params(url)
        self.cookie_dict = self.parse_cookies(self.headers.get("Cookie", ""))

    def parse_url_params(self, url):
        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)

    def parse_cookies(self, cookie_str):
        cookies = {}
        if cookie_str:
            cookie_pairs = cookie_str.split("; ")
            for pair in cookie_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    cookies[key] = value
        return cookies

    def to_dict(self):
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "cookies": self.cookies,
            "user_agent": self.user_agent,
            "protocol_version": self.protocol_version,
            "url_params": self.url_params,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        request_line = f"{self.method} {self.url} {self.protocol_version}"
        headers = "\n".join([f"{key}: {value}" for key, value in self.headers.items()])
        cookies = "; ".join([f"{key}={value}" for key, value in self.cookies.items()])
        body = self.body if self.body else ""
        return f"{request_line}\n{headers}\n\nCookies: {cookies}\n\n{body}"

class HTTPResponse:
    def __init__(self, status_line, headers=None, body=None):
        self.status_line = status_line
        self.headers = headers if headers is not None else {}
        self.body = body
        self.cookies = self.parse_cookies(self.headers.get("Set-Cookie", ""))

    def parse_cookies(self, cookie_str):
        cookies = {}
        if cookie_str:
            cookie_pairs = cookie_str.split(", ")
            for pair in cookie_pairs:
                parts = pair.split(";")[0].split("=", 1)
                if len(parts) == 2:
                    key, value = parts
                    cookies[key] = value
        return cookies

    def to_dict(self):
        return {
            "status_line": self.status_line,
            "headers": self.headers,
            "body": self.body,
            "cookies": self.cookies,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        headers = "\n".join([f"{key}: {value}" for key, value in self.headers.items()])
        cookies = "; ".join([f"{key}={value}" for key, value in self.cookies.items()])
        body = self.body if self.body else ""
        return f"{self.status_line}\n{headers}\n\nCookies: {cookies}\n\n{body}"

def parse_http_response(raw_response):
    # 응답을 줄 단위로 나눕니다.
    lines = raw_response.split("\n")
    
    # 상태 줄과 헤더를 분리합니다.
    status_line = lines[0]
    headers = {}
    body = ""
    is_body = False
    
    for line in lines[1:]:
        if is_body:
            body += line + "\n"
        elif line == "":
            is_body = True
        else:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
    
    response = HTTPResponse(status_line, headers, body)
    return response

# 주어진 HTTP 응답 패킷
raw_response = """HTTP/1.1 200 OK
Date: Sun, 02 Jun 2024 07:37:33 GMT
Expires: -1
Cache-Control: private, max-age=0
Content-Type: text/html; charset=ISO-8859-1
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-9Xoh0yslWpco6d7p8JxQ1Q' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
P3P: CP="This is not a P3P policy! See g.co/p3phelp for more info."
Content-Encoding: gzip
Server: gws
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Set-Cookie: 1P_JAR=2024-06-02-07; expires=Tue, 02-Jul-2024 07:37:33 GMT; path=/; domain=.google.com; Secure, AEC=AQTF6HxHTgR6_lpfDKIdT7OnjogUM9vu7kbT-CK1KvwJivdTkkk2U3Uo0A; expires=Fri, 29-Nov-2024 07:37:33 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax, NID=514=xCsUPAKbvuxzZCSznvx6HnmoTDKFqWjrGLvgCm53BKJAXfPHs_AuHCwkcR-Ea4l00Kwmdy_--GMg7x0Z8lJX5HO1-Z2Ln-Xq3kXsHkZZ_gOmYEZ1iP5fNjs6TbL8RrMuNrEnzA8xsRDXsKS7uXAB1t5AY-SYbI64_Rvlwh98NDY; expires=Mon, 02-Dec-2024 07:37:33 GMT; path=/; domain=.google.com; HttpOnly
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
Transfer-Encoding: chunked

<!doctype html><html itemscope="" itemtype="http://schema.org/WebPage" lang="ko"><head><meta content="text/html; charset=UTF-8" http-equiv="Content-Type"><meta content="/images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"><title>Google</title><script nonce="9Xoh0yslWpco6d7p8JxQ1Q">(function(){var _g={kEI:'PSFcZq_IGpSLvr0PhZ66MQ',kEXPI:'0,3700249,1061,79,538656,2872,2891,8348,3406,31274,30022,16335,107242,6636,49751,2,39761,6699,41949,57734,2,2,1,24626,2006,8155,23351,8702,13733,9779,42459,20199,6049,67129,3030,15816,1804,26408,20674,340,1294,42267,5225878,891,622,39,5991769,2839992,23938433,4043710,16673,43886,3,318,4,1281,3,2124363,23029351,7954,1,4844,8409,10754,135,5197,2,576,28027,36870,1922,8578,2,9,2370,6407,2952,5097,5796,10475,4690,7981,201,390,5545,5744,9660,11915,16175,10085,11585,6754,155,399,1288,797,4400,5225,3879,3896,3839,9,6591,1426,1113,968,539,1643,1450,207,121,2648,569,4,123,293,2588,4278,1,303,5,11,2962,4,614,1187,3,977,72,3450,3,1721,2718,224,1549,519,890,3518,3,2732,246,1494,4044,96,1295,321,1528,2,470,732,575,405,595,447,993,654,465,3,417,890,441,96,81,425,2669,2217,15,2,1504,3,1417,3,5,971,712,1030,891,253,561,2,2,585,38,4,214,12,32,883,241,172,1403,328,1729,688,258,119,53,690,581,151,232,376,20,63,120,3211,1930,333,509,6,1858,1380,2178,223,243,466,596,34,539,22,2274,549,465,664,236,2,140,230,374,217,44,409,302,292,3,45,24,364,108,162,1223,258,198,800,89,616,26,282,207,165,39,488,128,2,836,159,139,81,266,141,135,859,56,5,3,8,278,1113,394,513,303,245,309,991,97,1,3,73,208,1128,367,131,80,105,275,243,21219463,361370,4267,3,5250,3045,2288,3586,1993,1421,608',kBL:'Cfkd',kOPI:89978449};(function(){var a;(null==(a=window.google)?0:a.stvsc)?google.kEI=_g.kEI:window.google=_g;}).call(this);})();(function(){google.sn='webhp';google.kHL='ko';})();(function(){
var h=this||self;function l(){return void 0!==window.google&&void 0!==window.google.kOPI&&0!==window.google.kOPI?window.google.kOPI:null};var m,n=[];function p(a){for(var b;a&&(!a.getAttribute||!(b=a.getAttribute("eid")));)a=a.parentNode;return b||m}function q(a){for(var b=null;a&&(!a.getAttribute||!(b=a.getAttribute("leid")));)a=a.parentNode;return b}function r(a){/^http:/i.test(a)&&"https:"===window.location.protocol&&(google.ml&&google.ml(Error("a"),!1,{src:a,glmm:1}),a="");return a}
function t(a,b,c,d,k){var e="";-1===b.search("&ei=")&&(e="&ei="+p(d),-1===b.search("&lei=")&&(d=q(d))&&(e+="&lei="+d));d="";var g=-1===b.search("&cshid=")&&"slh"!==a,f=[];f.push(["zx",Date.now().toString()]);h._cshid&&g&&f.push(["cshid",h._cshid]);c=c();null!=c&&f.push(["opi",c.toString()]);for(c=0;c<f.length;c++){if(0===c||0<c)d+="&";d+=f[c][0]+"="+f[c][1]}return"/"+(k||"gen_204")+"?atyp=i&ct="+String(a)+"&cad="+(b+e+d)};m=google.kEI;google.getEI=p;google.getLEI=q;google.ml=function(){return null};google.log=function(a,b,c,d,k,e){e=void 0===e?l:e;c||(c=t(a,b,e,d,k));if(c=r(c)){a=new Image;var g=n.length;n[g]=a;a.onerror=a.onload=a.onabort=function(){delete n[g]};a.src=c}};google.logUrl=function(a,b){b=void 0===b?l:b;return t("",a,b)};}).call(this);(function(){google.y={};google.sy=[];google.x=function(a,b){if(a)var c=a.id;else{do c=Math.random();while(google.y[c])}google.y[c]=[a,b];return!1};google.sx=function(a){google.sy.push(a)};google.lm=[];google.plm=function(a){google.lm.push.apply(google.lm,a)};google.lq=[];google.load=function(a,b,c){google.lq.push([[a],b,c])};google.loadAll=function(a,b){google.lq.push([a,b])};google.bx=!1;google.lx=function(){};var d=[];google.fce=function(a,b,c,e){d.push([a,b,c,e])};google.qce=d;}).call(this);google.f={};(function(){
document.documentElement.addEventListener("submit",function(b){var a;if(a=b.target){var c=a.getAttribute("data-submitfalse");a="1"===c||"q"===c&&!a.elements.q.value?!0:!1}else a=!1;a&&(b.preventDefault(),b.stopPropagation())},!0);document.documentElement.addEventListener("click",function(b){var a;a:{for(a=b.target;a&&a!==document.documentElement;a=a.parentElement)if("A"===a.tagName){a="1"===a.getAttribute("data-nohref");break a}a=!1}a&&b.preventDefault()},!0);}).call(this);</script><style>#gbar,#guser{font-size:13px;padding-top:1px !重要한;}#gbar{height:22px}#guser{padding-bottom:7px !重要한;text-align:right}.gbh,.gbd{border-top:1px solid #c9d7f1;font-size:1px}.gbh{height:0;position:absolute;top:24px;width:100%}@media all{.gb1{height:22px;margin-right:.5em;vertical-align:top}#gbar{float:left}}a.gb1,a.gb4{text-decoration:underline !重要한}a.gb1,a.gb4{color:#00c !重要한}.gbi .gb4{color:#dd8e27 !重要한}.gbf .gb4{color:#900 !重要한}
</style><style>body,td,a,p,.h{font-family:&#44404;&#47548;,&#46027;&#50880;,arial,sans-serif}.ko{font-size:9pt}body{margin:0;overflow-y:scroll}#gog{padding:3px 8px 0}td{line-height:.8em}.gac_m td{line-height:17px}form{margin-bottom:20px}.h{color:#1967d2}em{font-weight:bold;font-style:normal}.lst{height:25px;width:496px}.gsfi,.lst{font:18px arial,sans-serif}.gsfs{font:17px arial,sans-serif}.ds{display:inline-box;display:inline-block;margin:3px 0 4px;margin-left:4px}input{font-family:inherit}body{background:#fff;color:#000}a{color:#681da8;text-decoration:none}a:hover,a:active{text-decoration:underline}.fl a{color:#1967d2}a:visited{color:#681da8}.sblc{padding-top:5px}.sblc a{display:block;margin:2px 0;margin-left:13px;font-size:11px}.lsbb{background:#f8f9fa;border:solid 1px;border-color:#dadce0 #70757a #70757a #dadce0;height:30px}.lsbb{display:block}#WqQANb a{display:inline-block;margin:0 12px}.lsb{background:url(/images/nav_logo229.png) 0 -261px repeat-x;color:#000;border:none;cursor:pointer;height:30px;margin:0;outline:0;font:15px arial,sans-serif;vertical-align:top}.lsb:active{background:#dadce0}.lst:focus{outline:none}.Ucigb{width:458px}</style><script nonce="9Xoh0yslWpco6d7p8JxQ1Q">(function(){window.google.erd={jsr:1,bv:2018,de:true};
var h=this||self;var k,l=null!=(k=h.mei)?k:1,n,p=null!=(n=h.sdo)?n:!重要한,p=0,q,r,t=google.erd,v=t.jsr;google.ml=function(a,b,d,m,e){e=void 0===e?2:e;b&&(r=a&&a.message);void 0===d&&(d={});d.cad="ple_"+google.ple+".aple_"+google.aple;if(google.dl)return google.dl(a,e,d,!0),null;b=d;if(0>v){window.console&&console.error(a,b);if(-2===v)throw a;b=!1}else b=!a||!a.message||"Error loading script"===a.message||p>=l&&!m?!0:!1;if(!b)return null;p++;d=d||{};b=encodeURIComponent;var c="/gen_204?atyp=i&ei="+b(google.kEI);google.kEXPI&&(c+="&jexpid="+b(google.kEXPI));c+="&srcpg="+b(google.sn)+"&jsr="+b(t.jsr)+
"&bver="+b(t.bv);var f=a.lineNumber;void 0!==f&&(c+="&line="+f);var g=a.fileName;g&&(0<g.indexOf("-extension:/")&&(e=3),c+="&script="+b(g),f&&g===window.location.href&&(f=document.documentElement.outerHTML.split("\n")[f],c+="&cad="+b(f?f.substring(0,300):"No script found.")));google.ple&&1===google.ple&&(e=2);c+="&jsel="+e;for(var u in d)c+="&",c+=b(u),c+="=",c+=b(d[u]);c=c+"&emsg="+b(a.name+": "+a.message);c=c+"&jsst="+b(a.stack||"N/A");12288<=c.length&&(c=c.substr(0,12288));a=c;m||google.log(0,"",a);return a};window.onerror=function(a,b,d,m,e){r!==a&&(a=e instanceof Error?e:Error(a),void 0===d||"lineNumber"in a||(a.lineNumber=d),void 0===b||"fileName"in a||(a.fileName=b),google.ml(a,!重要한,void 0,!重要한,"SyntaxError"===a.name||"SyntaxError"===a.message.substring(0,11)||-1!==a.message.indexOf("Script error")?3:0));r=null;p&&q>=l&&(window.onerror=null)};})();</script><body>"""

response = parse_http_response(raw_response)
print(response.to_json())
