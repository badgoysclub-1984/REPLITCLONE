package com.replitclone.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Bolt
import androidx.compose.material.icons.rounded.Code
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Folder
import androidx.compose.material.icons.rounded.Memory
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ElevatedButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.replitclone.app.ui.theme.ReplitCloneTheme
import kotlinx.coroutines.delay

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ReplitCloneTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    ReplitCloneScreen()
                }
            }
        }
    }
}

data class CodeFile(
    val path: String,
    var content: String
)

@Composable
fun ReplitCloneScreen() {
    val files = remember {
        mutableStateListOf(
            CodeFile(
                "main.py",
                """
                def greet(name: str):
                    return f"Hello, {name}!"

                if __name__ == "__main__":
                    print(greet("Replit"))
                """.trimIndent()
            ),
            CodeFile(
                "utils/math.py",
                """
                def fib(n):
                    a, b = 0, 1
                    for _ in range(n):
                        a, b = b, a + b
                    return a
                """.trimIndent()
            ),
            CodeFile(
                "README.md",
                "# Replit Clone\n\nTap Run to execute a simulated build."
            )
        )
    }

    var selectedIndex by remember { mutableStateOf(0) }
    var runOutput by remember { mutableStateOf("Ready. Press Run.") }
    var isRunning by remember { mutableStateOf(false) }
    val activeFile = files[selectedIndex]

    LaunchedEffect(isRunning) {
        if (isRunning) {
            runOutput = "[10:14:08] Installing dependencies..."
            delay(650)
            runOutput += "\n[10:14:09] Booting compute container (python-3.12)..."
            delay(700)
            runOutput += "\n[10:14:10] Running ${activeFile.path}"
            delay(850)
            runOutput += "\n\nHello, Replit!"
            runOutput += "\nFibonacci(10) = 55"
            runOutput += "\n\n[10:14:11] Process exited with code 0"
            isRunning = false
        }
    }

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .windowInsetsPadding(WindowInsets.statusBars)
                .windowInsetsPadding(WindowInsets.navigationBars)
                .windowInsetsPadding(WindowInsets.ime)
                .padding(horizontal = 12.dp, vertical = 10.dp)
        ) {
            val isCompact = maxWidth < 700.dp
            val consoleHeight by animateDpAsState(targetValue = if (isRunning) 220.dp else 180.dp, label = "consoleHeight")

            if (isCompact) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    WorkspaceHeader(
                        selectedFile = activeFile.path,
                        isRunning = isRunning,
                        onRunClick = {
                        if (!isRunning) {
                            runOutput = ""
                            isRunning = true
                        }
                    }
                    )
                    FileStrip(files = files, selectedIndex = selectedIndex, onSelect = { selectedIndex = it })
                    EditorPane(
                        modifier = Modifier.weight(1f),
                        file = activeFile,
                        onContentChange = { files[selectedIndex] = activeFile.copy(content = it) }
                    )
                    OutputPane(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(consoleHeight),
                        output = runOutput
                    )
                }
            } else {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    WorkspaceHeader(
                        selectedFile = activeFile.path,
                        isRunning = isRunning,
                        onRunClick = {
                        if (!isRunning) {
                            runOutput = ""
                            isRunning = true
                        }
                    }
                    )
                    Row(
                        modifier = Modifier.fillMaxSize(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        FileExplorer(
                            modifier = Modifier
                                .fillMaxHeight()
                                .width(250.dp),
                            files = files,
                            selectedIndex = selectedIndex,
                            onSelect = { selectedIndex = it }
                        )
                        Column(
                            modifier = Modifier
                                .fillMaxHeight()
                                .weight(1f),
                            verticalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            FileStrip(files = files, selectedIndex = selectedIndex, onSelect = { selectedIndex = it })
                            EditorPane(
                                modifier = Modifier.weight(1f),
                                file = activeFile,
                                onContentChange = { files[selectedIndex] = activeFile.copy(content = it) }
                            )
                            OutputPane(modifier = Modifier.height(consoleHeight), output = runOutput)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun WorkspaceHeader(selectedFile: String, isRunning: Boolean, onRunClick: () -> Unit) {
    val runColor by animateColorAsState(
        targetValue = if (isRunning) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.primary,
        label = "runButtonColor"
    )
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerHigh),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text("Replit Clone", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    Text(
                        "Focused coding workspace",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                ElevatedButton(
                    onClick = onRunClick,
                    enabled = !isRunning,
                    colors = CardDefaults.elevatedCardColors(
                        containerColor = runColor,
                        contentColor = MaterialTheme.colorScheme.onPrimary
                    ).let {
                        androidx.compose.material3.ButtonDefaults.elevatedButtonColors(
                            containerColor = runColor,
                            contentColor = MaterialTheme.colorScheme.onPrimary
                        )
                    },
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Rounded.PlayArrow, contentDescription = null)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(if (isRunning) "Running" else "Run")
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                StatChip(icon = Icons.Rounded.Code, label = "Active", value = selectedFile.substringAfterLast('/'))
                StatChip(icon = Icons.Rounded.Memory, label = "Memory", value = "420 MB")
                StatChip(icon = Icons.Rounded.Schedule, label = "Latency", value = "42 ms")
            }
        }
    }
}

@Composable
private fun StatChip(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, value: String) {
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        tonalElevation = 0.dp
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Icon(icon, contentDescription = null, modifier = Modifier.size(16.dp), tint = MaterialTheme.colorScheme.secondary)
            Text(
                "$label: $value",
                style = MaterialTheme.typography.labelMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
private fun FileExplorer(
    modifier: Modifier,
    files: List<CodeFile>,
    selectedIndex: Int,
    onSelect: (Int) -> Unit
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(Icons.Rounded.Folder, contentDescription = null)
                Text("Workspace", style = MaterialTheme.typography.titleSmall)
            }
            HorizontalDivider()
            LazyColumn(modifier = Modifier.fillMaxSize()) {
                items(files.indices.toList()) { index ->
                    val item = files[index]
                    val selected = selectedIndex == index
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                if (selected) MaterialTheme.colorScheme.surfaceVariant
                                else MaterialTheme.colorScheme.surface
                            )
                            .clickable { onSelect(index) }
                            .padding(horizontal = 12.dp, vertical = 10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(Icons.Rounded.Description, contentDescription = null)
                        Text(item.path, style = MaterialTheme.typography.bodyMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                }
            }
        }
    }
}

@Composable
private fun FileStrip(
    files: List<CodeFile>,
    selectedIndex: Int,
    onSelect: (Int) -> Unit
) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
        files.forEachIndexed { index, file ->
            FilterChip(
                selected = selectedIndex == index,
                onClick = { onSelect(index) },
                label = { Text(file.path.substringAfterLast('/')) },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = MaterialTheme.colorScheme.primary,
                    selectedLabelColor = MaterialTheme.colorScheme.onPrimary
                ),
                leadingIcon = {
                    if (selectedIndex == index) {
                        Icon(Icons.Rounded.Bolt, contentDescription = null, modifier = Modifier.size(16.dp))
                    }
                }
            )
        }
    }
}

@Composable
private fun EditorPane(
    modifier: Modifier,
    file: CodeFile,
    onContentChange: (String) -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(file.path, style = MaterialTheme.typography.titleSmall)
                Text("UTF-8", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            HorizontalDivider()
            Row(modifier = Modifier.fillMaxSize()) {
                val codeLines = file.content.lines().size.coerceAtLeast(1)
                Column(
                    modifier = Modifier
                        .fillMaxHeight()
                        .width(44.dp)
                        .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.25f))
                        .padding(top = 14.dp),
                    verticalArrangement = Arrangement.spacedBy(2.dp),
                    horizontalAlignment = Alignment.End
                ) {
                    repeat(codeLines) { idx ->
                        Text(
                            text = (idx + 1).toString(),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(end = 8.dp)
                        )
                    }
                }
                BasicTextField(
                    value = file.content,
                    onValueChange = onContentChange,
                    textStyle = MaterialTheme.typography.bodyMedium.copy(
                        fontFamily = FontFamily.Monospace,
                        color = MaterialTheme.colorScheme.onSurface
                    ),
                    cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                    decorationBox = { innerTextField ->
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(14.dp)
                        ) {
                            if (file.content.isEmpty()) {
                                Text(
                                    "Start coding...",
                                    style = TextStyle(
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        fontFamily = FontFamily.Monospace
                                    )
                                )
                            }
                            innerTextField()
                        }
                    },
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                )
            }
        }
    }
}

@Composable
private fun OutputPane(modifier: Modifier, output: String) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerHigh)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    "Console",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    "Python 3.12",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.secondary
                )
            }
            HorizontalDivider()
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(10.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .border(
                        width = 1.dp,
                        color = MaterialTheme.colorScheme.outlineVariant,
                        shape = RoundedCornerShape(12.dp)
                    )
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(12.dp)
            ) {
                Text(
                    text = output,
                    style = MaterialTheme.typography.bodySmall.copy(fontFamily = FontFamily.Monospace),
                    color = MaterialTheme.colorScheme.onSurface
                )
            }
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF0D1320)
@Composable
private fun ReplitClonePreview() {
    ReplitCloneTheme {
        ReplitCloneScreen()
    }
}
