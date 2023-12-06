# Set working directory
$DIR = $PSScriptRoot

# Constants
$DYNAMIC_THEME_NAME = "dynamic"
$THEME_FILE_EXTENSION = "-color-theme.json"
$DYNAMIC_PALETTE_FILENAME = "dynamic-palette.txt"
$TEMPLATE_THEME_FILENAME = "viiv-color-theme.template"
$BASE_COLOR_TOTAL = 10
$GRADATIONAL_TOTAL = 30

# Generate palette colors
Function GeneratePaletteColors { 
	$palette = python -c "from peelee.peelee import Palette; palette = Palette($BASE_COLOR_TOTAL, $GRADATIONAL_TOTAL).generate_palette(); print(palette)"
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