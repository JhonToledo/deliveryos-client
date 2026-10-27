# DeliveryOS Client (app Android del cliente)

## Que es
Shell de Capacitor que carga el marketplace en vivo: `server.url` = `https://deliveryosapp.com/stores` (`capacitor.config.json`). Paquete `com.deliveryosapp.client`, repo `github.com/JhonToledo/deliveryos-client`. Version actual: `versionCode 1` / `1.0`.
**Toda la UI vive en el backend** (repo `deliveryos`, `templates/client/stores.html`, `track.html`, `account.html`). Cambios de HTML/CSS/JS/backend NO requieren recompilar. Lee primero el `CLAUDE.md` del repo `deliveryos` (reglas generales, dark mode, paleta, sin guion largo).

## ESTADO: bloqueada a proposito hasta el lanzamiento
`COMING_SOON=1` en produccion, y esta app **no lleva `?bypass=`** en su `server.url` por decision del usuario (2026-09-04): `/stores` es justo lo que el gate oculta y un bypass embebido en el APK lo expondria a cualquiera con el archivo. Hoy el WebView muestra "Proximamente". **No tocar `capacitor.config.json` ni distribuir este APK sin que el usuario lo pida.** Cuando llegue el lanzamiento, lo mas simple es poner `COMING_SOON=0` en el servidor (no agregar el bypass).

## Que aporta lo nativo (pendiente de construir)
- Hoy solo trae `@capacitor/push-notifications` instalado, sin integracion: el backend no guarda token FCM del cliente (`Customer` no tiene `fcm_token`) ni envia push de estado del pedido. El cliente solo recibe cambios en tiempo real con la pagina abierta (Socket.IO) y por WhatsApp.
- Pendiente: columna `Customer.fcm_token` + migracion, `POST /api/customer/fcm-token`, `_capSetupPush()` en `stores.html` (copiar el patron de `admin/dashboard.html`), push en confirmado/listo/en camino/entregado y mensajes del chat con el rider, deep link a `/track/<token>`.
- El pago con tarjeta (Paybox de PagoPlux, iframe) ya se probo dentro de un WebView de Capacitor. Brave Shields o adblockers pueden bloquear el iframe sin dejar rastro.

## Reglas
- Antes de agregar push: canal Android propio con id versionado (los canales son inmutables) y `appendUserAgent: DeliveryOSClient/<build>` para distinguir builds, igual que admin y rider.
- `node_modules/` e `.idea/` no se versionan.

## Compilar (Windows, sin Android Studio)
```bash
export JAVA_HOME="$LOCALAPPDATA/Programs/jdk/jdk-21.0.12.1+1"
export ANDROID_HOME="$LOCALAPPDATA/Android/Sdk"
npx cap sync android
cd android && ./gradlew.bat assembleDebug --no-daemon     # APK en android/app/build/outputs/apk/debug/
```
En un equipo nuevo falta `android/local.properties`: `sdk.dir=C:/Users/<usuario>/AppData/Local/Android/Sdk`. Entorno completo (JDK 21 con jlink, SDK 36, sdkmanager) en el CLAUDE.md de `deliveryos`, seccion "Compilacion de las apps". Firebase: `android/app/google-services.json` (proyecto "deliveryosapp").

## Flujo de trabajo
Documenta aqui todo cambio nativo. Commits en espanol, primera linea maximo 72 caracteres.
