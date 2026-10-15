package com.example.slnelauncher.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val SloneColorScheme = darkColorScheme(
    primary = SloneGold,
    onPrimary = SloneBlack,
    secondary = SloneTitaniumCard,
    onSecondary = SloneTextPrimary,
    tertiary = SloneGoldBright,
    background = SloneBlack,
    onBackground = SloneTextPrimary,
    surface = SloneTitaniumDark,
    onSurface = SloneTextPrimary
)

@Composable
fun SLNELauncherTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = SloneColorScheme,
        typography = Typography,
        content = content
    )
}
