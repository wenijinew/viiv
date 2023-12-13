# Test Code
# > for($i=1;$i -lt 500; $i++){pwsh -File .\viiv.ps1; Write-Output $i; Start-Sleep -Seconds 20 }

# Set working directory
$DIR = $PSScriptRoot

# Constants
$DYNAMIC_THEME_NAME = "dynamic"
$THEME_FILE_EXTENSION = "-color-theme.json"
$DYNAMIC_PALETTE_FILENAME = "dynamic-palette.txt"
$TEMPLATE_THEME_FILENAME = "viiv-color-theme.template.json"
$BASE_COLOR_TOTAL = 10
$GRADATIONAL_TOTAL = 60 
$DARK_COLOR_GRADATIONAL_TOTAL = 60 
$GENERAL_MAX_COLOR = 100 
$DARK_MAX_COLOR = 20
$DARK_BASE_COLORS = "['#030313']"

# Generate palette colors
Function GeneratePaletteColors { 
	$palette = python -c "from peelee.peelee import Palette; palette = Palette($BASE_COLOR_TOTAL, $GRADATIONAL_TOTAL, $DARK_COLOR_GRADATIONAL_TOTAL, $GENERAL_MAX_COLOR, $DARK_MAX_COLOR, $DARK_BASE_COLORS).generate_palette(); print(palette)"
	Select-String -Pattern 'C_\d{2}_\d{2}:#[A-Fa-f0-9]{6}' -InputObject $palette -AllMatches | ForEach-Object {$_.Matches} | ForEach-Object {$_.Value} | Set-Content "$DIR\themes\$DYNAMIC_PALETTE_FILENAME"
}

# Replace colors in file
Function ReplaceColors {
	Param(
		[string]$TargetFile,
		[string]$PaletteFile = "$DIR\themes\$DYNAMIC_PALETTE_FILENAME"
	)
	$TemplateContent = Get-Content $TargetFile
	Get-Content $PaletteFile | ForEach-Object { 
		$colorName = $_.Split(":")[0] 
		$colorValue = $_.Split(":")[1]
		$TemplateContent = $($TemplateContent -replace "$colorName", "$colorValue")
	}
	Set-Content -Path $TargetFile -Value $TemplateContent
}

# Create dynamic theme file
Function CreateDynamicThemeFile {
	Push-Location "$DIR\themes"

	GeneratePaletteColors

	$dynamicThemeFileName = "$DYNAMIC_THEME_NAME$THEME_FILE_EXTENSION"

	If (Test-Path $dynamicThemeFileName) { 
		Remove-Item $dynamicThemeFileName
	}

	Copy-Item $TEMPLATE_THEME_FILENAME $dynamicThemeFileName

	ReplaceColors $dynamicThemeFileName

	Pop-Location
}

CreateDynamicThemeFile