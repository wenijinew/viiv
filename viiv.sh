#!/usr/bin/env bash
_DIR="$(cd "$(dirname "$0")" && pwd)"

EXIT_SUCCESS=0

DYNAMIC_THEME_NAME="dynamic"
THEME_FILE_EXTENSION="-color-theme.json"
DYNAMIC_PALETTE_FILENAME="dynamic-palette.txt"
TEMPLATE_THEME_FILENAME="viiv-color-theme.template"

# by default, we generate 10 base colors and 16 gradations for each base color
BASE_COLOR_TOTAL=1
GRADATIONS_TOTAL=16

# call python module to generate palette file
generate_palette_colors(){
    palette=$(python -c "from peelee.peelee import Palette; palette = Palette(${BASE_COLOR_TOTAL}, ${GRADATIONS_TOTAL}).generate_palette(); print(palette)")
    echo "$palette" | grep -iEo 'C(_[[:digit:]]{1,}){2}\:#[[:alnum:]]{6}' > "${DYNAMIC_PALETTE_FILENAME}"
}

replace_color(){
    target_file="${1}"
    palette_file="${2:-${DYNAMIC_PALETTE_FILENAME}}"
    while read -r _color;do
          color_name="$(echo "${_color}" | cut -d':' -f1)"
          color_value="$(echo "${_color}" | cut -d':' -f2)"
          sed -i "s/${color_name}/${color_value}/g" "${target_file}"
    done < "${_DIR}/${palette_file}"
}

create_dynamic_theme_file(){
	pushd $_DIR/themes
	generate_palette_colors
    dynamic_theme_file_name="${DYNAMIC_THEME_NAME}${THEME_FILE_EXTENSION}"
    if [ -e "${dynamic_theme_file_name}" ];then
       rm -f "${dynamic_theme_file_name}"
    fi
    cp "${TEMPLATE_THEME_FILENAME}" "${dynamic_theme_file_name}"
    replace_color "${dynamic_theme_file_name}"
	popd
}

while getopts "t:" opt; do
    case $opt in
        t) DYNAMIC_THEME_NAME="${OPTARG}" ;;
        *) usage; exit "${EXIT_SUCCESS}" ;;
    esac
done

create_dynamic_theme_file