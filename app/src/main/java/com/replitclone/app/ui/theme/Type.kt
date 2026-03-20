package com.replitclone.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val Typography = Typography(
	titleLarge = TextStyle(
		fontFamily = FontFamily.Serif,
		fontWeight = FontWeight.Bold,
		fontSize = 24.sp,
		lineHeight = 30.sp,
		letterSpacing = 0.sp
	),
	titleMedium = TextStyle(
		fontFamily = FontFamily.Serif,
		fontWeight = FontWeight.SemiBold,
		fontSize = 20.sp,
		lineHeight = 26.sp
	),
	bodyMedium = TextStyle(
		fontFamily = FontFamily.SansSerif,
		fontWeight = FontWeight.Normal,
		fontSize = 14.sp,
		lineHeight = 20.sp,
		letterSpacing = 0.2.sp
	),
	bodySmall = TextStyle(
		fontFamily = FontFamily.Monospace,
		fontWeight = FontWeight.Normal,
		fontSize = 12.sp,
		lineHeight = 16.sp
	),
	labelMedium = TextStyle(
		fontFamily = FontFamily.SansSerif,
		fontWeight = FontWeight.Medium,
		fontSize = 12.sp,
		lineHeight = 16.sp,
		letterSpacing = 0.3.sp
	)
)
