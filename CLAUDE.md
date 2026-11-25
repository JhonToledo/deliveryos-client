# DeliveryOS Client (app Android del cliente)

## Que es
Shell de Capacitor que carga el marketplace en vivo: `server.url` = `https://deliveryosapp.com/stores` (`capacitor.config.json`). Paquete `com.deliveryosapp.client`, repo `github.com/JhonToledo/deliveryos-client`. Version actual: `versionCode 2` / `1.1` (nombre visible **DeliveryOS**, con el logo propio; ver "Icono, nombre y pantalla de carga").
**Toda la UI vive en el backend** (repo `deliveryos`, `templates/client/stores.html`, `track.html`, `account.html`). Cambios de HTML/CSS/JS/backend NO requieren recompilar. Lee primero el `CLAUDE.md` del repo `deliveryos` (reglas generales, dark mode, paleta, sin guion largo).

## ESTADO: la tienda ya esta abierta (2026-11-23), la app funciona
Hasta el 2026-11-22 esta app estuvo bloqueada a proposito: con `COMING_SOON=1` el WebView solo mostraba "Proximamente" y **no lleva `?bypass=`** en su `server.url` por decision del usuario (2026-09-04), porque un bypass embebido en el APK habria expuesto `/stores` a cualquiera con el archivo. El 2026-11-23 se paso el servidor a `COMING_SOON=0` ("pon todo en produccion") y ahora `/stores` carga normal: **sigue sin agregarse el bypass** (ya no hace falta; si algun dia se vuelve a cerrar la tienda con `COMING_SOON=1`, esta app volveria a mostrar "Proximamente"). El APK de debug 1.1 se genero el 2026-11-24 a pedido del usuario y queda tambien en `deliveryos/apk/` (carpeta ignorada por git del repo `deliveryos`).

## Permisos de ubicacion (2026-11-25)
- **Falla**: «Usar mi ubicacion actual» decia «Permiso de ubicacion denegado» sin preguntar nada. La app 1.1 (codigo 2, APK y AAB) no declaraba ningun permiso de ubicacion. `BridgeWebChromeClient.onGeolocationPermissionsShowPrompt` de Capacitor ya pide `ACCESS_COARSE_LOCATION` y `ACCESS_FINE_LOCATION`, pero Android niega sin preguntar lo que el manifest no declara.
- **Arreglo** (`AndroidManifest.xml`): los dos permisos (solo con la app en pantalla, sin segundo plano) y `uses-feature` de ubicacion con `required="false"` para que Play no oculte la app a equipos sin GPS. Verificado con `aapt2 dump permissions` y `dump badging`. **Probado en BlueStacks** (2026-11-25): Android pregunta, y negar o permitir funciona. Ojo: con la web de hoy el boton puede no llenar la direccion aunque se permita (pide la ubicacion aproximada, que en BlueStacks y en telefonos sin la «precision de la ubicacion» de Google no responde); lo arregla el cambio web `_gpsDireccion` (commit `084e836` del repo `deliveryos`, sin desplegar).
- **Al subirlo a Play**: la app ahora pide ubicacion, asi que el formulario «Seguridad de los datos» debe declarar ubicacion aproximada y precisa (opcional, para el funcionamiento de la app).
- El AAB de codigo 2 **no debe enviarse a revision**.
- La web (repo `deliveryos`) tiene un cambio aparte, sin desplegar: aviso claro cuando se niega el permiso, visible tambien dentro de los mapas, y en la app no se pide el GPS apenas se abre.

## Google y Facebook dentro de la app (2026-11-25, opcion A decidida por el dueno)
- **Falla**: «Continuar con Google/Facebook» abria el navegador del telefono y la sesion se quedaba alla.
- **Parte de Android (commit `5cf4bb7`)**: enlace propio `com.deliveryosapp.client://oauth` (segundo `intent-filter` de `MainActivity`, que es `singleTask`; en iOS `CFBundleURLTypes`), `@capacitor/app` y `@capacitor/browser`, y `plugins.App.disableBackButtonHandler: true` (sin eso el plugin App cambiaria el boton atras).
- **Probado en BlueStacks**: el enlace llega con la app abierta (sin recargar) y cerrada; `Capacitor.Plugins.Browser.open` abre Chrome encima de la app y se vuelve con un boton o solo; la pestana se cierra sola al volver.
- **Trampas**: tras recargar la pagina `App.getLaunchUrl()` sigue devolviendo el enlace viejo, y con la app cerrada el enlace llega por `getLaunchUrl` Y por `appUrlOpen`: la web debe usarlo una sola vez.
- **Falta la parte web** (repo `deliveryos`): ver la seccion «App Android del cliente: ubicacion y Google dentro de la app» de su CLAUDE.md. La app 1.1 (codigo 2) instalada no tiene estas librerias: la web debe pedirle que actualice.
- Subir `versionCode` a 3 cuando la parte web este probada.
- **Probar el codigo web sin desplegar**: APK temporal con `server.url` a `http://127.0.0.1:<puerto>/stores`, `cleartext` y `usesCleartextTraffic`, mas `adb reverse`; despues `git status` debe quedar limpio y se reinstala el APK que apunta a produccion.

## Icono, nombre y pantalla de carga (2026-11-24)
- **Nombre visible**: `DeliveryOS` (`res/values/strings.xml`: `app_name` y `title_activity_main`; `appName` de `capacitor.config.json`).
- **Logo**: `C:\Users\jairo\Documents\Proyectos Python\logos\logo_solo.png` (dorado, fondo transparente) sobre azul medianoche `#1A202C` (paleta oficial). Se genero con `scripts/gen_icons.py` (Pillow): `python scripts/gen_icons.py android/app/src/main/res` crea los `mipmap-*` (`ic_launcher.png`, `ic_launcher_round.png` y el primer plano adaptativo `ic_launcher_foreground.png`, con el logo dentro de la zona segura de 66 dp) y las pantallas de carga `drawable*/splash.png` (mismas medidas que las de Capacitor). El fondo del icono adaptativo es `res/values/ic_launcher_background.xml` (`#1A202C`). Para cambiar el logo, reemplazar el archivo y volver a correr el script.
- La pantalla de carga (`splash.png`) era la de Capacitor por defecto (cruz azul sobre blanco): ahora es el logo centrado sobre `#1A202C`. No hay plugin de splash instalado.
- No tiene icono monocromatico (Android 13 con iconos tematicos mostrara el normal).

## Que aporta lo nativo (pendiente de construir)
- Hoy solo trae `@capacitor/push-notifications` instalado, sin integracion: el backend no guarda token FCM del cliente (`Customer` no tiene `fcm_token`) ni envia push de estado del pedido. El cliente solo recibe cambios en tiempo real con la pagina abierta (Socket.IO) y por WhatsApp.
- Pendiente: columna `Customer.fcm_token` + migracion, `POST /api/customer/fcm-token`, `_capSetupPush()` en `stores.html` (copiar el patron de `admin/dashboard.html`), push en confirmado/listo/en camino/entregado y mensajes del chat con el rider, deep link a `/track/<token>`.
- El pago con tarjeta (Paybox de PagoPlux, iframe) ya se probo dentro de un WebView de Capacitor. Brave Shields o adblockers pueden bloquear el iframe sin dejar rastro.

## Reglas
- Antes de agregar push: canal Android propio con id versionado (los canales son inmutables) y `appendUserAgent: DeliveryOSClient/<build>` para distinguir builds, igual que admin y rider.
- `node_modules/` e `.idea/` no se versionan.

## Compilar (Windows, sin Android Studio)
```bash
export JAVA_HOME="$LOCALAPPDATA/Programs/jdk/jdk-21.0.12.1+1"   # en esta PC (2026-11-24): C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot
export ANDROID_HOME="$LOCALAPPDATA/Android/Sdk"
npx cap sync android
cd android && ./gradlew.bat assembleDebug --no-daemon     # APK en android/app/build/outputs/apk/debug/
```
En un equipo nuevo falta `android/local.properties`: `sdk.dir=C:/Users/<usuario>/AppData/Local/Android/Sdk`. Entorno completo (JDK 21 con jlink, SDK 36, sdkmanager) en el CLAUDE.md de `deliveryos`, seccion "Compilacion de las apps". Firebase: `android/app/google-services.json` (proyecto "deliveryosapp").

## Firma de lanzamiento para Google Play (paso M17, 2026-11-24)
- Play pide un `.aab` firmado; un APK de depuracion no sirve. Con Play App Signing la llave nuestra es la **llave de subida** (la definitiva la guarda Google).
- **Una sola llave para las tres apps**: `C:\Users\jairo\DeliveryOS-firma-android\deliveryos-subida.jks` (alias `upload`, RSA 4096, valida hasta 2054), FUERA de todo repositorio. La contraseña la eligio el dueño y no esta en ningun archivo: nunca pedirla en el chat ni pasarla escrita en un comando. Huella SHA-256 del certificado (publica): `4D:90:1C:FC:2F:58:7E:5D:E1:2E:7C:26:58:7D:4F:8A:CB:87:23:0C:14:A8:DE:36:B7:43:00:08:20:B0:B4:2C`.
- `build.gradle` no tiene `signingConfig` a proposito: se compila sin firmar y firma `C:\Users\jairo\DeliveryOS-firma-android\firmar.ps1`, que ejecuta **el dueño** (pide la contraseña en su terminal y la borra al terminar). Al lado hay un `LEEME.txt`.
- Version nueva: subir `versionCode` (Play no acepta dos veces el mismo) y `versionName` en `android/app/build.gradle` (y el numero de `appendUserAgent` si la app lo usa), `npx cap sync android`, `cd android && ./gradlew.bat clean bundleRelease --no-daemon`, y el dueño ejecuta `firmar.ps1`. El programa firma las TRES apps a la vez: las tres deben estar compiladas. Salen en `C:\Users\jairo\Documents\DeliveryOS-AAB\` junto con `verificacion-de-firma.txt`.
- `clean` borra `android/app/build`: antes, copiar cualquier APK que se quiera conservar.
- Primer paquete firmado (2026-11-24): `DeliveryOS-Cliente-1.1-codigo2.aab`. Revisado por dentro: paquete, version, API 36, no es de depuracion, abre la direccion correcta sin `?bypass` y esta firmado con la llave nueva. **No probado en un telefono**. Subirlo a Play Console lo hace el dueño.
- Un telefono con el APK de depuracion instalado debe **desinstalarlo** antes de instalar la app desde Play (la firma es distinta).
- `server.allowNavigation` entra en este paquete y **nunca se probo en un telefono**: antes de publicar, probar el pago con tarjeta con verificacion del banco (3DS) y que regrese a la app.

## Flujo de trabajo
Documenta aqui todo cambio nativo. Commits en espanol, primera linea maximo 72 caracteres.

## iOS (fase F7, 2026-11-24): proyecto creado en Windows, SIN compilar ni probar
**Estado**: la carpeta `ios/` existe (`npx cap add ios`: Capacitor 8 con Swift Package Manager, iOS 15 o superior) y está configurada, pero **nunca se ha abierto en Xcode ni compilado**: esta PC es Windows y no hay Mac. Bundle id `com.deliveryosapp.client`, nombre en pantalla «DeliveryOS», versión 1.0 (compilación 1). Nada de esto toca el APK de Android (excepto lo que se avisa abajo).
**Qué se configuró**:
- `ios/App/App/Info.plist`: permisos con texto en español (ubicación mientras se usa (dirección de entrega y cobertura)), modos en segundo plano (`remote-notification`) y `ITSAppUsesNonExemptEncryption = false`.
- `ios/App/App/App.entitlements` (`aps-environment` y (sin time-sensitive: los avisos del cliente no atraviesan No molestar)), enlazado en `project.pbxproj` (Debug y Release). El `aps-environment` queda en `development`; Xcode lo pasa a `production` al firmar para la App Store.
- `ios/App/App/AppDelegate.swift`: entrega al plugin de push el token (y el error) de registro; usa Firebase solo si está enlazado (ver «Push» abajo).
- `capacitor.config.json`: bloque `ios` (`contentInset: never`, porque las zonas seguras las maneja el sitio con `viewport-fit=cover`, y `appendUserAgent: DeliveryOSClient/ios-1`) y `server.allowNavigation` con `*.pagoplux.com` y `*.cardinalcommerce.com` (el reto 3DS del pago con tarjeta navega a esos sitios y vuelve; sin esto Capacitor los abriría fuera de la app).
- Icono (1024x1024 sin transparencia, como exige la App Store) y pantalla de carga con el logo sobre `#1A202C`, generados con `scripts/gen_ios_assets.py` (`python scripts/gen_ios_assets.py ios/App/App/Assets.xcassets`).
- `codemagic.yaml`: plantilla **sin probar** para compilar y subir a TestFlight desde la nube.
- Comprobado desde Windows (87 comprobaciones estáticas entre los 3 proyectos): llaves del `project.pbxproj` balanceadas, `Info.plist` y entitlements legibles, imágenes de las medidas correctas, `Package.swift` con Capacitor 8 y `codemagic.yaml` con sintaxis válida. **No se compiló nada.**
**Regla**: `ios/App/CapApp-SPM/Package.swift` lo regenera Capacitor en cada `npx cap sync` (no editarlo a mano) y apunta a los plugins dentro de `node_modules`: antes de compilar siempre `npm ci`. `ios/App/App/public` y `ios/App/App/capacitor.config.json` se generan con `npx cap sync ios` y no se versionan.

**Lo que falta (en este orden; nada de esto se puede hacer desde Windows)**:
1. **Cuenta de Apple Developer Program** (99 USD al año) y crear la app en App Store Connect con el bundle id `com.deliveryosapp.client` (de ahí sale el «Apple ID» numérico que pide `codemagic.yaml`).
2. **Compilar sin Mac**: Codemagic. Crear la integración con App Store Connect (clave de API `.p8` con rol App Manager), ponerle el nombre `DeliveryOS_ASC` (o cambiarlo en `codemagic.yaml`), poner `APP_STORE_APPLE_ID` y lanzar el flujo `ios-testflight`. La plantilla no se ha corrido nunca: el primer intento puede pedir ajustes (versión de Xcode, número de compilación, firma).
3. **Push (FCM)**: en Firebase (proyecto `deliveryosapp`) agregar una app iOS con el bundle id `com.deliveryosapp.client` y descargar `GoogleService-Info.plist`; subir la llave APNs (`.p8`) en Firebase > Configuración del proyecto > Cloud Messaging > Configuración de la app de Apple; y agregar al target `App` el paquete `https://github.com/firebase/firebase-ios-sdk` con el producto `FirebaseMessaging` y el plist como recurso (en Xcode: File > Add Package Dependencies; sin Mac se puede hacer editando `ios/App/App.xcodeproj/project.pbxproj`, trabajo que se hace desde Windows cuando se tenga el plist). **El `AppDelegate.swift` ya está listo**: usa Firebase solo si el paquete está enlazado y el plist existe (`#if canImport`). Sin esto la push entrega el token de APNs y el servidor lo rechaza con 400 `apns_token` (necesita el de FCM).
4. **Sonido de la alerta**: convertir `static/3_firma_doble.mp3` del repo `deliveryos` a `alerta_pedido.caf` (en una Mac `afconvert -f caff -d LEI16 3_firma_doble.mp3 alerta_pedido.caf`; con ffmpeg `-f caf`, máximo 30 s) y agregarlo al paquete de la app; sin él las ofertas y los pedidos nuevos suenan con el sonido normal de iOS (`send_push` arma el bloque APNs con `<sonido>.caf`).
5. **Probar** en el simulador y después en un iPhone real con TestFlight: isla y barra de inicio (el sitio usa `viewport-fit=cover` y `env(safe-area-inset-*)`; si se ve doble margen, revisar `contentInset`), teclado abierto (cómo reduce la pantalla), giro a horizontal, modo oscuro, notificación con la app cerrada y su sonido, el pago con tarjeta con 3DS y el inicio de sesión.
6. **App Store**: textos de privacidad («Privacidad de la app»), capturas, cuenta de prueba para el revisor y las guías de abajo.

**Riesgos propios de esta app (bloquean la App Store si no se resuelven)**:
- **Guía 4.8 (Sign in with Apple)**: el sitio ofrece entrar con Google y Facebook, así que Apple exige ofrecer también «Iniciar sesión con Apple». No existe en el sitio.
- **Google y Facebook no funcionan dentro de un WebView**: Google rechaza el inicio de sesión embebido (`disallowed_useragent`) y el inicio de sesión del sitio abre una ventana emergente (`window.open`) que el WebView no maneja. Habría que abrir el OAuth con el navegador del sistema (ASWebAuthenticationSession) o dejar solo correo y cédula en la app. Esto afecta igual a la app de Android del cliente (nunca se probó).
- **Guía 4.2**: la app es un envoltorio del sitio; pesa a favor que tendrá notificaciones nativas, pero **hoy la app del cliente no tiene push**: `Customer` no tiene `fcm_token` ni existe `POST /api/customer/fcm-token` (ver «Que aporta lo nativo»).
- **Guía 5.1.1(v)**: hay que poder eliminar la cuenta dentro de la app (hoy no existe esa opción).
