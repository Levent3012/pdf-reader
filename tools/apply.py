import os
p='altklausuren.html'; s=open(p,encoding='utf8').read()
if '__audioTTS' not in s:
    shim=open('tools/shim.html',encoding='utf8').read()
    i=s.find('<script>'); s=s[:i]+shim+s[i:]
    s=s.replace("n.textContent = msg + ' Lautlos-Schalter prüfen oder in Safari öffnen.';","n.textContent = msg + (window.__audioTTS ? ' Einmal auf Vorlesen tippen, damit der Browser Ton erlaubt.' : ' Lautlos-Schalter prüfen oder in Safari öffnen.');")
    open(p,'w',encoding='utf8').write(s); print('gepatcht')
else: print('schon gepatcht')
