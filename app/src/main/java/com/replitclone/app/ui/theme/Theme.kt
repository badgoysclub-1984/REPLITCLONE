package com.replitclone.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val AppDarkScheme = darkColorScheme(
    primary = Cyan500,
    secondary = Mint400,
    surface = Slate900,
    surfaceVariant = Slate800,
    background = Slate900,
    onPrimary = Slate900,
    onSurface = Ink100,
    onBackground = Ink100,
    onSurfaceVariant = Ink300
)

@Composable
fun ReplitCloneTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = AppDarkScheme,
        typography = Typography,
        content = content
    )
}
