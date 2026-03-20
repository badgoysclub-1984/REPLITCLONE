package com.replitclone.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val AppDarkScheme = darkColorScheme(
    primary = NeonBlue500,
    secondary = NeonBlue300,
    surface = Black900,
    surfaceVariant = Black850,
    background = Black950,
    onPrimary = Black950,
    onSurface = Ink100,
    onBackground = Ink100,
    onSurfaceVariant = Ink400
)

@Composable
fun ReplitCloneTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = AppDarkScheme,
        typography = Typography,
        content = content
    )
}
