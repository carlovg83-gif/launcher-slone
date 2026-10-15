package com.example.slnelauncher.ui.main

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.widget.Toast
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.focusable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.key.*
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.slnelauncher.R
import com.example.slnelauncher.theme.*
import kotlinx.coroutines.delay
import java.text.SimpleDateFormat
import java.util.*

enum class ActionType {
    APP, SETTINGS, BROWSER_LINK
}

data class LauncherAppItem(
    val id: String,
    val title: String,
    val subtitle: String,
    val packageName: String,
    val iconRes: Int,
    val accentColor: Color,
    val actionType: ActionType = ActionType.APP,
    val customUrl: String? = null
)

@Composable
fun MainScreen(modifier: Modifier = Modifier) {
    val context = LocalContext.current

    // Apps principales solicitadas en orden de prioridad
    val primaryApps = remember {
        listOf(
            LauncherAppItem(
                id = "smarttube",
                title = "SmartTube 4K",
                subtitle = "YouTube sin anuncios · 60 FPS",
                packageName = "org.smarttube.stable",
                iconRes = R.drawable.ic_smarttube,
                accentColor = SmartTubeRed
            ),
            LauncherAppItem(
                id = "tivimate",
                title = "TiviMate",
                subtitle = "Fútbol y Canales en Directo",
                packageName = "ar.tvplayer.tv",
                iconRes = R.drawable.ic_tivimate,
                accentColor = TiviMateBlue
            ),
            LauncherAppItem(
                id = "3cat",
                title = "3Cat",
                subtitle = "TV3 Directes en català",
                packageName = "cat.ccma.androidtv.tv3",
                iconRes = R.drawable.ic_3cat,
                accentColor = Cat3Red
            ),
            LauncherAppItem(
                id = "netflix",
                title = "Netflix",
                subtitle = "Cine y Series en 4K",
                packageName = "com.netflix.ninja",
                iconRes = R.drawable.ic_netflix,
                accentColor = NetflixRed
            ),
            LauncherAppItem(
                id = "rtve",
                title = "RTVE Play",
                subtitle = "La 1 UHD · Directos",
                packageName = "com.rtve.androidtv",
                iconRes = R.drawable.ic_rtve,
                accentColor = RtveBlue
            ),
            LauncherAppItem(
                id = "slone_browser",
                title = "SLÖNECast Web",
                subtitle = "Portal Kiosk de Salón",
                packageName = "com.tcl.browser",
                iconRes = R.drawable.ic_slone_browser,
                accentColor = SloneBrowserGold
            ),
            LauncherAppItem(
                id = "settings",
                title = "Ajustes TV",
                subtitle = "Sistema Xiaomi · Red y Pantalla",
                packageName = "com.android.tv.settings",
                iconRes = R.drawable.ic_settings,
                accentColor = SettingsGray,
                actionType = ActionType.SETTINGS
            )
        )
    }

    // Accesos rápidos de sintonización y soberanía
    val quickShortcuts = remember {
        listOf(
            LauncherAppItem(
                id = "tv3_directe",
                title = "TV3 en Directe",
                subtitle = "Emissió en viu sense talls",
                packageName = "cat.ccma.androidtv.tv3",
                iconRes = R.drawable.ic_3cat,
                accentColor = Cat3Red
            ),
            LauncherAppItem(
                id = "thinkpad_cast",
                title = "ThinkPad X390",
                subtitle = "Enlace directo local 192.168.1.145",
                packageName = "com.tcl.browser",
                iconRes = R.drawable.ic_slone_browser,
                accentColor = SloneGold,
                actionType = ActionType.BROWSER_LINK,
                customUrl = "http://192.168.1.145:8080"
            ),
            LauncherAppItem(
                id = "playstore",
                title = "Catálogo de Apps",
                subtitle = "Google Play Store TV",
                packageName = "com.android.vending",
                iconRes = R.drawable.ic_settings,
                accentColor = SloneGoldBright
            )
        )
    }

    // Reloj digital en tiempo real y fecha en castellano
    var currentTime by remember { mutableStateOf("") }
    var currentDate by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())
        val dateFormat = SimpleDateFormat("EEEE, d 'de' MMMM", Locale.getDefault())
        while (true) {
            val now = Date()
            currentTime = timeFormat.format(now)
            currentDate = dateFormat.format(now).replaceFirstChar { it.uppercase() }
            delay(1000)
        }
    }

    // Foco inicial automático en SmartTube 4K
    val firstAppFocusRequester = remember { FocusRequester() }
    LaunchedEffect(Unit) {
        delay(250)
        try {
            firstAppFocusRequester.requestFocus()
        } catch (_: Exception) {}
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(SloneBlack)
    ) {
        // Fondo oficial SLÖNE (Titanio ahumado + Corona + Dipolo Ö)
        Image(
            painter = painterResource(id = R.drawable.slone_wallpaper),
            contentDescription = "Fondo de pantalla oficial SLÖNE",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // Degradado cinemático para máxima legibilidad a 3 metros
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            Color(0xDD050507),
                            Color(0x88050507),
                            Color(0xEE050507)
                        )
                    )
                )
        )

        // Contenedor principal ajustado a la pantalla de 1080p sin scroll vertical
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 48.dp, vertical = 24.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // 1. BARRA SUPERIOR (Brand Header, Estado Soberano, Reloj)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Logotipo SLÖNE + Corona geométrica
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_slone_crown),
                        contentDescription = "Corona SLÖNE",
                        modifier = Modifier.size(34.dp)
                    )
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "SLÖNE",
                                color = SloneGoldBright,
                                fontSize = 23.sp,
                                fontWeight = FontWeight.ExtraBold,
                                letterSpacing = 3.sp,
                                fontFamily = FontFamily.SansSerif
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(Color(0x33FFD700))
                                    .padding(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "OS 1.0",
                                    color = SloneGoldGlow,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        Text(
                            text = "SISTEMA DE ENTRETENIMIENTO PRIVADO SOBERANO",
                            color = SloneTextSecondary,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium,
                            letterSpacing = 0.8.sp
                        )
                    }
                }

                // Píldora de estado de red
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(20.dp))
                        .background(Color(0x22FFFFFF))
                        .border(1.dp, Color(0x33FFD700), RoundedCornerShape(20.dp))
                        .padding(horizontal = 14.dp, vertical = 5.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(7.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF00FF66))
                        )
                        Text(
                            text = "SLÖNE FLUX · 192.168.1.135 · ACTIVO",
                            color = SloneTextPrimary,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            letterSpacing = 0.5.sp
                        )
                    }
                }

                // Reloj digital minimalista
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = currentTime.ifEmpty { "19:40" },
                        color = SloneTextPrimary,
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    Text(
                        text = currentDate.ifEmpty { "Jueves, 15 de octubre" },
                        color = SloneTextSecondary,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Normal
                    )
                }
            }

            // 2. HERO BILLBOARD COMPACTO
            HeroBillboard(
                onWatchNow = {
                    launchItem(context, primaryApps[1]) // TiviMate
                }
            )

            // 3. FILA DE APLICACIONES PRINCIPALES (Grandes, proporcionadas, con foco luminoso)
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Bottom
                ) {
                    Text(
                        text = "TUS APLICACIONES",
                        color = SloneTextPrimary,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.2.sp
                    )
                    Text(
                        text = "Navegación nativa con cruceta y botón central",
                        color = SloneTextMuted,
                        fontSize = 11.sp
                    )
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(18.dp)
                ) {
                    primaryApps.forEachIndexed { index, app ->
                        AppCard(
                            item = app,
                            focusRequester = if (index == 0) firstAppFocusRequester else null,
                            onClick = { launchItem(context, app) }
                        )
                    }
                }
            }

            // 4. FILA DE SINTONIZACIÓN RÁPIDA & HERRAMIENTAS
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "SINTONIZACIÓN RÁPIDA & HERRAMIENTAS",
                    color = SloneTextPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.8.sp
                )

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    quickShortcuts.forEach { shortcut ->
                        QuickCard(
                            item = shortcut,
                            onClick = { launchItem(context, shortcut) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun HeroBillboard(onWatchNow: () -> Unit) {
    var isFocused by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isFocused) 1.02f else 1.0f,
        animationSpec = tween(120),
        label = "heroScale"
    )
    val borderColor by animateColorAsState(
        targetValue = if (isFocused) SloneGoldGlow else Color(0x332A3040),
        animationSpec = tween(120),
        label = "heroBorder"
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(115.dp)
            .scale(scale)
            .clip(RoundedCornerShape(16.dp))
            .background(
                Brush.horizontalGradient(
                    colors = if (isFocused) {
                        listOf(Color(0xFF20283C), Color(0xFF181F32), Color(0xFF141926))
                    } else {
                        listOf(Color(0xF0141824), Color(0xD0181F30), Color(0xB0121622))
                    }
                )
            )
            .border(BorderStroke(if (isFocused) 3.dp else 1.dp, borderColor), RoundedCornerShape(16.dp))
            .onFocusChanged { isFocused = it.isFocused }
            .onKeyEvent { keyEvent ->
                if (keyEvent.type == KeyEventType.KeyUp && isDpadCenter(keyEvent)) {
                    onWatchNow()
                    true
                } else false
            }
            .focusable()
            .clickable { onWatchNow() }
            .padding(horizontal = 26.dp, vertical = 16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxSize(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.Center
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(4.dp))
                            .background(SloneGold)
                            .padding(horizontal = 6.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = "SINTONÍA PRIVADA",
                            color = SloneBlack,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.ExtraBold
                        )
                    }
                    Text(
                        text = "FÚTBOL Y DEPORTES EN DIRECTO · 4K 60FPS",
                        color = SloneTextSecondary,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        letterSpacing = 0.8.sp
                    )
                }

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = "CANALES & TRANSMISIÓN SIN ANUNCIOS",
                    color = SloneTextPrimary,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.5.sp
                )

                Text(
                    text = "SmartTube, TiviMate y 3Cat listos con un solo toque en tu mando a distancia.",
                    color = SloneTextSecondary,
                    fontSize = 11.sp
                )
            }

            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(10.dp))
                    .background(if (isFocused) SloneGold else Color(0x33FFFFFF))
                    .padding(horizontal = 20.dp, vertical = 10.dp)
            ) {
                Text(
                    text = if (isFocused) "ABRIR TIVIMATE [OK]" else "SINTONIZAR",
                    color = if (isFocused) SloneBlack else SloneTextPrimary,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.8.sp
                )
            }
        }
    }
}

@Composable
fun AppCard(
    item: LauncherAppItem,
    focusRequester: FocusRequester? = null,
    onClick: () -> Unit
) {
    var isFocused by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isFocused) 1.12f else 1.0f,
        animationSpec = tween(120),
        label = "cardScale"
    )
    val borderColor by animateColorAsState(
        targetValue = if (isFocused) SloneGoldGlow else Color(0x33444E66),
        animationSpec = tween(120),
        label = "cardBorder"
    )

    var cardModifier = Modifier
        .width(190.dp)
        .height(115.dp)
        .shadow(
            elevation = if (isFocused) 26.dp else 4.dp,
            shape = RoundedCornerShape(14.dp),
            spotColor = if (isFocused) SloneGoldGlow else Color.Transparent
        )
        .clip(RoundedCornerShape(14.dp))
        .background(
            Brush.verticalGradient(
                colors = if (isFocused) {
                    listOf(Color(0xFF2C364E), Color(0xFF1E2536))
                } else {
                    listOf(Color(0xDD161A24), Color(0xAA0F121A))
                }
            )
        )
        .border(
            BorderStroke(if (isFocused) 4.dp else 1.dp, borderColor),
            RoundedCornerShape(14.dp)
        )
        .onFocusChanged { isFocused = it.isFocused }

    if (focusRequester != null) {
        cardModifier = cardModifier.focusRequester(focusRequester)
    }

    cardModifier = cardModifier
        .onKeyEvent { keyEvent ->
            if (keyEvent.type == KeyEventType.KeyUp && isDpadCenter(keyEvent)) {
                onClick()
                true
            } else false
        }
        .focusable()
        .clickable { onClick() }
        .padding(14.dp)

    Column(
        modifier = Modifier
            .width(190.dp)
            .scale(scale),
        horizontalAlignment = Alignment.Start
    ) {
        Box(
            modifier = cardModifier,
            contentAlignment = Alignment.Center
        ) {
            Image(
                painter = painterResource(id = item.iconRes),
                contentDescription = item.title,
                modifier = Modifier.size(50.dp)
            )

            Box(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(item.accentColor)
            )
        }

        Spacer(modifier = Modifier.height(6.dp))

        Text(
            text = item.title,
            color = if (isFocused) SloneGoldGlow else SloneTextPrimary,
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold,
            maxLines = 1
        )

        Text(
            text = item.subtitle,
            color = if (isFocused) SloneTextPrimary else SloneTextMuted,
            fontSize = 11.sp,
            fontWeight = FontWeight.Normal,
            maxLines = 1
        )
    }
}

@Composable
fun QuickCard(
    item: LauncherAppItem,
    onClick: () -> Unit
) {
    var isFocused by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isFocused) 1.08f else 1.0f,
        animationSpec = tween(120),
        label = "quickScale"
    )
    val borderColor by animateColorAsState(
        targetValue = if (isFocused) SloneGoldGlow else Color(0x33444E66),
        animationSpec = tween(120),
        label = "quickBorder"
    )

    Row(
        modifier = Modifier
            .scale(scale)
            .width(245.dp)
            .height(60.dp)
            .shadow(
                elevation = if (isFocused) 18.dp else 2.dp,
                shape = RoundedCornerShape(12.dp),
                spotColor = if (isFocused) SloneGoldGlow else Color.Transparent
            )
            .clip(RoundedCornerShape(12.dp))
            .background(
                Brush.horizontalGradient(
                    colors = if (isFocused) {
                        listOf(Color(0xFF28344E), Color(0xFF1B2334))
                    } else {
                        listOf(Color(0xDD151822), Color(0x990E1017))
                    }
                )
            )
            .border(
                BorderStroke(if (isFocused) 3.dp else 1.dp, borderColor),
                RoundedCornerShape(12.dp)
            )
            .onFocusChanged { isFocused = it.isFocused }
            .onKeyEvent { keyEvent ->
                if (keyEvent.type == KeyEventType.KeyUp && isDpadCenter(keyEvent)) {
                    onClick()
                    true
                } else false
            }
            .focusable()
            .clickable { onClick() }
            .padding(horizontal = 14.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Image(
            painter = painterResource(id = item.iconRes),
            contentDescription = item.title,
            modifier = Modifier.size(32.dp)
        )

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = item.title,
                color = if (isFocused) SloneGoldGlow else SloneTextPrimary,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
                maxLines = 1
            )
            Text(
                text = item.subtitle,
                color = if (isFocused) SloneTextPrimary else SloneTextMuted,
                fontSize = 10.sp,
                maxLines = 1
            )
        }
    }
}

private fun isDpadCenter(keyEvent: KeyEvent): Boolean {
    val nativeCode = keyEvent.nativeKeyEvent.keyCode
    return nativeCode == android.view.KeyEvent.KEYCODE_DPAD_CENTER ||
            nativeCode == android.view.KeyEvent.KEYCODE_ENTER ||
            nativeCode == android.view.KeyEvent.KEYCODE_NUMPAD_ENTER
}

private fun launchItem(context: Context, item: LauncherAppItem) {
    when (item.actionType) {
        ActionType.SETTINGS -> {
            try {
                val intent = Intent(Settings.ACTION_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(intent)
            } catch (_: Exception) {
                Toast.makeText(context, "No se pudo abrir Ajustes", Toast.LENGTH_SHORT).show()
            }
        }
        ActionType.APP -> {
            val pm = context.packageManager
            // En Android TV, priorizar LeanbackLaunchIntent y luego LaunchIntent
            val intent = pm.getLeanbackLaunchIntentForPackage(item.packageName)
                ?: pm.getLaunchIntentForPackage(item.packageName)
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(intent)
            } else {
                try {
                    val marketIntent = Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=${item.packageName}"))
                    marketIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(marketIntent)
                } catch (_: Exception) {
                    Toast.makeText(context, "${item.title} no está instalada", Toast.LENGTH_SHORT).show()
                }
            }
        }
        ActionType.BROWSER_LINK -> {
            val url = item.customUrl ?: "http://192.168.1.145:8080"
            try {
                val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                browserIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(browserIntent)
            } catch (_: Exception) {
                val pm = context.packageManager
                val intent = pm.getLeanbackLaunchIntentForPackage(item.packageName)
                    ?: pm.getLaunchIntentForPackage(item.packageName)
                if (intent != null) {
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(intent)
                } else {
                    Toast.makeText(context, "No se pudo abrir el navegador", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
