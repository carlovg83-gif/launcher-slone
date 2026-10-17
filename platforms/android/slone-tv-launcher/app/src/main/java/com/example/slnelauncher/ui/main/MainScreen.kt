package com.example.slnelauncher.ui.main

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.widget.Toast
import androidx.activity.compose.BackHandler
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
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
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
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.input.key.*
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.graphics.drawable.toBitmap
import com.example.slnelauncher.R
import com.example.slnelauncher.theme.*
import com.example.slnelauncher.ui.player.PlayerScreen
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

enum class ActionType {
    APP, SETTINGS, BROWSER_LINK, ALL_APPS_DRAWER, NATIVE_PLAYER
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

data class DiscoveredAppItem(
    val packageName: String,
    val label: String,
    val iconBitmap: ImageBitmap? = null
)

@Composable
fun MainScreen(modifier: Modifier = Modifier) {
    val context = LocalContext.current

    // Estado para el cajón / catálogo dinámico de aplicaciones
    var isAppsDrawerOpen by remember { mutableStateOf(false) }
    var installedApps by remember { mutableStateOf<List<DiscoveredAppItem>>(emptyList()) }
    var isLoadingApps by remember { mutableStateOf(false) }

    // Estado para el reproductor nativo Media3
    var activeStreamUrl by remember { mutableStateOf<String?>(null) }
    var activeStreamTitle by remember { mutableStateOf<String?>(null) }

    // Manejar retroceso con D-pad [BACK]
    BackHandler(enabled = isAppsDrawerOpen || activeStreamUrl != null) {
        if (activeStreamUrl != null) {
            activeStreamUrl = null
        } else {
            isAppsDrawerOpen = false
        }
    }

    // Cargar aplicaciones cuando se abre el cajón
    LaunchedEffect(isAppsDrawerOpen) {
        if (isAppsDrawerOpen) {
            isLoadingApps = true
            installedApps = loadInstalledApps(context)
            isLoadingApps = false
        }
    }

    // Apps principales universales sin sesgos regionales ni de marca
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
                subtitle = "IPTV Soberano · Directos UHD",
                packageName = "ar.tvplayer.tv",
                iconRes = R.drawable.ic_tivimate,
                accentColor = TiviMateBlue
            ),
            LauncherAppItem(
                id = "vlc",
                title = "VLC Media",
                subtitle = "Reproductor Universal Red & USB",
                packageName = "org.videolan.vlc",
                iconRes = R.drawable.ic_vlc,
                accentColor = VlcOrange
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
                subtitle = "Televisión Pública UHD",
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
                subtitle = "Configuración · Red y Pantalla",
                packageName = "com.android.tv.settings",
                iconRes = R.drawable.ic_settings,
                accentColor = SettingsGray,
                actionType = ActionType.SETTINGS
            )
        )
    }

    // Accesos rápidos y herramientas universales
    val quickShortcuts = remember {
        listOf(
            LauncherAppItem(
                id = "all_apps",
                title = "Catálogo de Apps",
                subtitle = "Todas las apps instaladas en TV",
                packageName = "",
                iconRes = R.drawable.ic_apps_grid,
                accentColor = SloneGoldBright,
                actionType = ActionType.ALL_APPS_DRAWER
            ),
            LauncherAppItem(
                id = "native_tv",
                title = "Televisión UHD Soberana",
                subtitle = "Emisión directa sin apps externas",
                packageName = "",
                iconRes = R.drawable.ic_smarttube,
                accentColor = SloneGoldBright,
                actionType = ActionType.NATIVE_PLAYER,
                customUrl = "https://rtvelivestream.rtve.es/rtvesec/la1/la1_main_dvr.m3u8"
            ),
            LauncherAppItem(
                id = "web_browser_clean",
                title = "Navegador Web",
                subtitle = "Buscador y Streaming sin Anuncios",
                packageName = "org.mozilla.tv.firefox",
                iconRes = R.drawable.ic_slone_browser,
                accentColor = SloneGold,
                actionType = ActionType.BROWSER_LINK,
                customUrl = "https://www.google.com"
            ),
            LauncherAppItem(
                id = "playstore",
                title = "Play Store TV",
                subtitle = "Instalar nuevas herramientas",
                packageName = "com.android.vending",
                iconRes = R.drawable.ic_settings,
                accentColor = SloneGold
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

                // Píldora de estado universal (sin IPs fijas)
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
                            text = "SLÖNE FLUX · PROTECCIÓN ACTIVA",
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

            // 2. HERO BILLBOARD COMPACTO (Sintonización Nativa con ExoPlayer)
            HeroBillboard(
                onWatchNow = {
                    activeStreamUrl = "https://rtvelivestream.rtve.es/rtvesec/tdp/tdp_main_dvr.m3u8"
                    activeStreamTitle = "Teledeporte 4K UHD"
                }
            )

            // 3. FILA DE APLICACIONES PRINCIPALES
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
                            onClick = {
                                launchItem(
                                    context = context,
                                    item = app,
                                    onOpenDrawer = { isAppsDrawerOpen = true },
                                    onOpenNativePlayer = { url, title ->
                                        activeStreamUrl = url
                                        activeStreamTitle = title
                                    }
                                )
                            }
                        )
                    }
                }
            }

            // 4. FILA DE SINTONIZACIÓN RÁPIDA & HERRAMIENTAS
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "ACCESOS RÁPIDOS & HERRAMIENTAS",
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
                            onClick = {
                                launchItem(
                                    context = context,
                                    item = shortcut,
                                    onOpenDrawer = { isAppsDrawerOpen = true },
                                    onOpenNativePlayer = { url, title ->
                                        activeStreamUrl = url
                                        activeStreamTitle = title
                                    }
                                )
                            }
                        )
                    }
                }
            }
        }

        // 5. CAJÓN DE TODAS LAS APLICACIONES INSTALADAS (DRAWER DINÁMICO)
        if (isAppsDrawerOpen) {
            AllAppsDrawer(
                apps = installedApps,
                isLoading = isLoadingApps,
                onClose = { isAppsDrawerOpen = false },
                onLaunchApp = { packageName ->
                    launchPackage(context, packageName)
                    isAppsDrawerOpen = false
                }
            )
        }

        // 6. REPRODUCTOR NATIVO DE VÍDEO (EXOPLAYER MEDIA3)
        if (activeStreamUrl != null) {
            PlayerScreen(
                streamUrl = activeStreamUrl!!,
                channelTitle = activeStreamTitle ?: "Emisión en Directo",
                onClosePlayer = { activeStreamUrl = null }
            )
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
                        text = "ENTRETENIMIENTO UNIVERSAL Y DEPORTES EN DIRECTO · 4K 60FPS",
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
                    text = "SmartTube, TiviMate y streaming sin anuncios listos con un solo toque en tu mando a distancia.",
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
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )

        Text(
            text = item.subtitle,
            color = if (isFocused) SloneTextPrimary else SloneTextMuted,
            fontSize = 11.sp,
            fontWeight = FontWeight.Normal,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
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
            .width(255.dp)
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
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            Text(
                text = item.subtitle,
                color = if (isFocused) SloneTextPrimary else SloneTextMuted,
                fontSize = 10.sp,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
fun AllAppsDrawer(
    apps: List<DiscoveredAppItem>,
    isLoading: Boolean,
    onClose: () -> Unit,
    onLaunchApp: (String) -> Unit
) {
    val firstAppFocusRequester = remember { FocusRequester() }

    LaunchedEffect(apps) {
        if (apps.isNotEmpty()) {
            delay(150)
            try {
                firstAppFocusRequester.requestFocus()
            } catch (_: Exception) {}
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xF5050508))
            .padding(horizontal = 48.dp, vertical = 24.dp)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Cabecera del Cajón
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_apps_grid),
                        contentDescription = "Catálogo de Apps",
                        modifier = Modifier.size(32.dp)
                    )
                    Column {
                        Text(
                            text = "CATÁLOGO DE APLICACIONES INSTALADAS",
                            color = SloneGoldBright,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.ExtraBold,
                            letterSpacing = 1.5.sp
                        )
                        Text(
                            text = if (isLoading) "Escaneando aplicaciones del sistema..." else "${apps.size} aplicaciones disponibles · Acceso directo sin publicidad",
                            color = SloneTextSecondary,
                            fontSize = 11.sp
                        )
                    }
                }

                // Botón visual para cerrar
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color(0x33FFFFFF))
                        .clickable { onClose() }
                        .padding(horizontal = 14.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = "[VOLVER / ATRÁS]",
                        color = SloneTextPrimary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Cuadrícula de Apps
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "Cargando aplicaciones instaladas...",
                        color = SloneGold,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            } else if (apps.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "No se encontraron aplicaciones adicionales.",
                        color = SloneTextSecondary,
                        fontSize = 14.sp
                    )
                }
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Fixed(5),
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    modifier = Modifier.fillMaxSize()
                ) {
                    itemsIndexed(apps) { index, app ->
                        DrawerAppCard(
                            app = app,
                            focusRequester = if (index == 0) firstAppFocusRequester else null,
                            onClick = { onLaunchApp(app.packageName) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun DrawerAppCard(
    app: DiscoveredAppItem,
    focusRequester: FocusRequester? = null,
    onClick: () -> Unit
) {
    var isFocused by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isFocused) 1.08f else 1.0f,
        animationSpec = tween(120),
        label = "drawerCardScale"
    )
    val borderColor by animateColorAsState(
        targetValue = if (isFocused) SloneGoldGlow else Color(0x333A4255),
        animationSpec = tween(120),
        label = "drawerCardBorder"
    )

    var cardModifier = Modifier
        .scale(scale)
        .fillMaxWidth()
        .height(110.dp)
        .shadow(
            elevation = if (isFocused) 18.dp else 2.dp,
            shape = RoundedCornerShape(12.dp),
            spotColor = if (isFocused) SloneGoldGlow else Color.Transparent
        )
        .clip(RoundedCornerShape(12.dp))
        .background(
            Brush.verticalGradient(
                colors = if (isFocused) {
                    listOf(Color(0xFF242E44), Color(0xFF182030))
                } else {
                    listOf(Color(0xEE141722), Color(0xCC0D1018))
                }
            )
        )
        .border(
            BorderStroke(if (isFocused) 3.dp else 1.dp, borderColor),
            RoundedCornerShape(12.dp)
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
        .padding(12.dp)

    Column(
        modifier = cardModifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (app.iconBitmap != null) {
            Image(
                bitmap = app.iconBitmap,
                contentDescription = app.label,
                modifier = Modifier.size(44.dp)
            )
        } else {
            Image(
                painter = painterResource(id = R.drawable.ic_settings),
                contentDescription = app.label,
                modifier = Modifier.size(44.dp)
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = app.label,
            color = if (isFocused) SloneGoldGlow else SloneTextPrimary,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            textAlign = TextAlign.Center
        )

        Text(
            text = app.packageName,
            color = SloneTextMuted,
            fontSize = 9.sp,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            textAlign = TextAlign.Center
        )
    }
}

private fun isDpadCenter(keyEvent: KeyEvent): Boolean {
    val nativeCode = keyEvent.nativeKeyEvent.keyCode
    return nativeCode == android.view.KeyEvent.KEYCODE_DPAD_CENTER ||
            nativeCode == android.view.KeyEvent.KEYCODE_ENTER ||
            nativeCode == android.view.KeyEvent.KEYCODE_NUMPAD_ENTER
}

private fun launchItem(
    context: Context,
    item: LauncherAppItem,
    onOpenDrawer: () -> Unit,
    onOpenNativePlayer: (String, String) -> Unit
) {
    when (item.actionType) {
        ActionType.ALL_APPS_DRAWER -> {
            onOpenDrawer()
        }
        ActionType.NATIVE_PLAYER -> {
            val url = item.customUrl ?: "https://rtvelivestream.rtve.es/rtvesec/la1/la1_main_dvr.m3u8"
            onOpenNativePlayer(url, item.title)
        }
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
            launchPackage(context, item.packageName, item.title)
        }
        ActionType.BROWSER_LINK -> {
            val url = item.customUrl ?: "https://www.google.com"
            try {
                val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                browserIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(browserIntent)
            } catch (_: Exception) {
                launchPackage(context, item.packageName, item.title)
            }
        }
    }
}

private fun launchPackage(context: Context, packageName: String, title: String? = null) {
    val pm = context.packageManager
    val intent = pm.getLeanbackLaunchIntentForPackage(packageName)
        ?: pm.getLaunchIntentForPackage(packageName)
    if (intent != null) {
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    } else {
        try {
            val marketIntent = Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=$packageName"))
            marketIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(marketIntent)
        } catch (_: Exception) {
            val appName = title ?: packageName
            Toast.makeText(context, "$appName no está disponible", Toast.LENGTH_SHORT).show()
        }
    }
}

suspend fun loadInstalledApps(context: Context): List<DiscoveredAppItem> = withContext(Dispatchers.IO) {
    val pm = context.packageManager
    val leanbackIntent = Intent(Intent.ACTION_MAIN, null).apply {
        addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER)
    }
    val standardIntent = Intent(Intent.ACTION_MAIN, null).apply {
        addCategory(Intent.CATEGORY_LAUNCHER)
    }

    val leanbackApps = pm.queryIntentActivities(leanbackIntent, 0)
    val standardApps = pm.queryIntentActivities(standardIntent, 0)
    val allActivities = (leanbackApps + standardApps).distinctBy { it.activityInfo.packageName }

    allActivities
        .filter { it.activityInfo.packageName != context.packageName }
        .map { resolveInfo ->
            val label = resolveInfo.loadLabel(pm).toString()
            val pkg = resolveInfo.activityInfo.packageName
            val drawable = try {
                resolveInfo.activityInfo.loadBanner(pm)
                    ?: resolveInfo.activityInfo.loadIcon(pm)
                    ?: resolveInfo.loadIcon(pm)
            } catch (_: Exception) {
                null
            }
            val bitmap = drawable?.let { d ->
                try {
                    d.toBitmap(width = 96, height = 96).asImageBitmap()
                } catch (_: Exception) {
                    null
                }
            }
            DiscoveredAppItem(
                packageName = pkg,
                label = label,
                iconBitmap = bitmap
            )
        }
        .sortedBy { it.label.lowercase() }
}
