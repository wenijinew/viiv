# Change Log

All notable changes to the "eu-vscode" extension will be documented in this file.

## [v0.2.35] - 2024-01-08

- Support both dark and light mode with one configuration(`config.json`)
- Pre-configured themes name could be configured in 'options'
- The option 'theme_mode' in options is optional. If it's not configured, then theme mode will be random - could be dark or light.
- The option 'theme_mode' in pre-configured themes is required - the pre-configured theme must be DARK or LIGHT.
- The option parameters are tuned to be the best. No need to make more changes unless the change can generate better themes.
- To have lighter workbench color, increase values of 'workbench_colors_min' and 'workbench_colors_max'. Normally, it's not necessary to change other parameters.

fe62d29 - 2024-01-08 08:01:23 - wenijinew@gmail.com - The property 'theme_mode' is required for pre-configured themes. Otherwise, the theme_mode will be randomly decided and it could be light which is not expected for pre-configured dark themes. (HEAD -> main, origin/np)
d7b2dea - 2024-01-08 06:55:17 - wenijinew@gmail.com - Dark and Light modes look perfect
58fc120 - 2024-01-08 06:21:42 - wenijinew@gmail.com - Fixed tab.inactiveBackground in LIGHT mode
d1253f7 - 2024-01-08 05:36:25 - wenijinew@gmail.com - Workbench color tuning is good for both dark and light mode
83a2481 - 2024-01-07 21:29:05 - wenijinew@gmail.com - Keep lightness as 0.35 if it's bigger than 0.35 for light mode
e1b8389 - 2024-01-07 18:28:22 - wenijinew@gmail.com - set fontStyle as bold if light mode
151d7b4 - 2024-01-07 13:37:17 - wenijinew@gmail.com - Workable solution to have one configuration to adapt both dark and light mode  
c5cd9f1 - 2024-01-07 13:27:34 - wenijinew@gmail.com - Better light mode configuration
6cc8e01 - 2024-01-07 07:45:51 - wenijinew@gmail.com - Support ligth mode. User can generate random theme and it could be dark or light
theme. #125

## [v0.2.32] - 2024-01-06

18ecfe2 - 2024-01-06 08:41:45 - wenijinew@gmail.com - #110 cleanup code about default themes - map  
bbf3e8f - 2024-01-05 15:15:26 - wenijinew@gmail.com - Tune 'default' area in config.json (origin/main, origin/HEAD)
7840203 - 2024-01-05 15:15:26 - wenijinew@gmail.com - Fix typo  
1544f34 - 2024-01-05 15:15:26 - wenijinew@gmail.com - Uplift peelee to v0.2.8  
0ea1606 - 2024-01-05 15:15:26 - wenijinew@gmail.com - Tune configuration for editorOverviewRuler  
fa11ebb - 2024-01-05 15:15:26 - wenijinew@gmail.com - #109 make hardcoded values in python script configurable i..

## [v0.2.31] - 2024-01-04

908b091 - 2024-01-04 17:07:37 - wenijinew@gmail.com - v0.2.31  
525d401 - 2024-01-04 17:02:03 - wenijinew@gmail.com - Add smoke-test for push and pull-request  
847b2d1 - 2024-01-04 17:02:03 - wenijinew@gmail.com - Fix bug caused by recursive function discarding red dark c..
f4d5967 - 2024-01-04 15:31:31 - wenijinew@gmail.com - Uplift peelee to 0.2.5. Tuning parameters. Better themes e..
6fbe07b - 2024-01-04 12:40:37 - wenijinew@gmail.com - Uplift peelee to 0.2.4.  
7930ecf - 2024-01-04 09:24:27 - wenijinew@gmail.com - decoration color use workbench light color by default. the..
084878c - 2024-01-04 09:24:27 - wenijinew@gmail.com - Add more built-in themes

## [v0.2.28] - 2024-01-04

375c039 - 2024-01-04 05:12:27 - wenijinew@gmail.com - v0.2.28 - uplift peelee to 0.2.3  
187c7b2 - 2024-01-04 04:26:04 - wenijinew@gmail.com - Remove dynamic theme.Use random-[0-7] as random themes. (tag: v0.2.27)

## [v0.2.27] - 2024-01-04

2ba964c - 2024-01-04 04:20:09 - wenijinew@gmail.com - v0.2.27  
c31a8b1 - 2024-01-04 04:17:59 - wenijinew@gmail.com - Improve workbench color theme  
d721d60 - 2024-01-03 21:21:05 - wenijinew@gmail.com - Highlight active border. Assert theme is None when printin.. (tag: v0.2.26)
17c66c6 - 2024-01-03 19:54:16 - wenijinew@gmail.com - Set border to dark color. Regenerate themes. Add twitter-d..
ded5279 - 2024-01-02 22:46:55 - wenijinew@gmail.com - Tune alpha range for selection, hover, highlight backgroun..
29924be - 2024-01-02 22:25:20 - wenijinew@gmail.com - Tune input border and background  
1ba33cf - 2024-01-02 22:13:21 - wenijinew@gmail.com - Tune color. Support decoration groups. Regenerate themes. (tag: v0.2.25)
74d1375 - 2023-12-27 09:31:58 - wenijinew@gmail.com - Regenerate themes (tag: v0.2.24)
1cf0e0f - 2023-12-27 09:31:58 - wenijinew@gmail.com - Fix makefile comment

## [v0.2.23] - 2023-12-27

5c293e4 - 2023-12-27 06:28:59 - wenijinew@gmail.com - v0.2.23 - Fix PowerShell comments (tag: v0.2.23)
e4e6097 - 2023-12-27 06:09:46 - wenijinew@gmail.com - Tune template to add new scope for block comment (tag: v0.2.22)

## [v0.2.21] - 2023-12-23

a73078f - 2023-12-23 16:35:26 - wenijinew@gmail.com - v0.2.21 (tag: v0.2.21)
296269b - 2023-12-23 16:32:23 - wenijinew@gmail.com - Fix hover foreground issue

## [v0.2.20] - 2023-12-23

0e7e0db - 2023-12-23 16:20:47 - wenijinew@gmail.com - v0.2.20 (tag: v0.2.20)
4ec9cea - 2023-12-23 16:20:47 - wenijinew@gmail.com - Merge ericsson-black and github-blue into default themes  
9125fae - 2023-12-23 15:59:19 - wenijinew@gmail.com - Fix viiv.py code issues (tag: v0.2.19)

## [v0.2.19] - 2023-12-23

2664100 - 2023-12-23 15:46:55 - wenijinew@gmail.com - v0.2.19  
25d9b07 - 2023-12-23 15:45:12 - wenijinew@gmail.com - Add logic to generate customized themes  
87c0338 - 2023-12-23 15:42:35 - wenijinew@gmail.com - Add logic to generate customized themes  
fc4e337 - 2023-12-23 14:39:34 - wenijinew@gmail.com - Fix testing\* colors

## [v0.2.18] - 2023-12-23

e6738dc - 2023-12-23 12:06:45 - wenijinew@gmail.com - v0.2.18 Add Ericsson Black theme (tag: v0.2.18)
e43d6a9 - 2023-12-23 09:23:28 - wenijinew@gmail.com - Generate dynamic theme when release. Add it in workflow. (tag: v0.2.17)
c006afe - 2023-12-23 09:23:28 - wenijinew@gmail.com - Fix random-blue. Add github-blue  
c5cb20c - 2023-12-23 08:57:17 - wenijinew@gmail.com - Fix terminalCommandDecoration.errorBackground (tag: v0.2.16)
de2b02c - 2023-12-23 08:57:17 - wenijinew@gmail.com - Fix terminalCommandDecoration.errorBackground  
c75388a - 2023-12-23 08:57:17 - wenijinew@gmail.com - Fix terminalCommandDecoration.successBackground  
821c9b5 - 2023-12-23 08:57:17 - wenijinew@gmail.com - Uplift peelee 0.2.2 and add random theme files  
4aebfa8 - 2023-12-23 07:44:03 - wenijinew@gmail.com - Provide two different sets of default themes. Dark and nor.. (tag: v0.2.15)
aaea0b5 - 2023-12-22 21:29:59 - wenijinew@gmail.com - Tune default themes color. Parameters of random theme dark.. (tag: v0.2.14)
f9d68a4 - 2023-12-22 13:51:45 - wenijinew@gmail.com - Regenerate violet theme  
6161b42 - 2023-12-22 13:49:14 - wenijinew@gmail.com - Set decoration group and use stable basic range to have th..
32050cc - 2023-12-22 13:04:13 - wenijinew@gmail.com - Refine gitDecoration. Separate yellow and orange which cou..
1ed2795 - 2023-12-22 12:44:32 - wenijinew@gmail.com - Tune diffEdior. gitDecoration  
563201d - 2023-12-22 12:40:18 - wenijinew@gmail.com - Tune diffEdior. gitDecoration  
fdadb38 - 2023-12-22 08:34:33 - wenijinew@gmail.com - Refine diffEditor  
ec748d4 - 2023-12-22 07:44:35 - wenijinew@gmail.com - Tuning diffEditor. inactive icon foreground  
2ff63a1 - 2023-12-21 20:58:11 - wenijinew@gmail.com - Tuning diffEditor  
e098a41 - 2023-12-21 20:58:11 - wenijinew@gmail.com - Fix editorHint foreground and hide editorHint border

## [v0.2.13] - 2023-12-21

425c86f - 2023-12-21 14:31:28 - wenijinew@gmail.com - v0.2.13 (tag: v0.2.13)
2fa59cc - 2023-12-21 14:26:48 - wenijinew@gmail.com - Fixed warnings in viiv.py  
59e0e42 - 2023-12-21 14:26:48 - wenijinew@gmail.com - Fix debugToolBar.background by using darker magenta  
897d6d3 - 2023-12-21 14:26:48 - wenijinew@gmail.com - Fix editorInfo bg and border

## [v0.2.12] - 2023-12-21

ee8d9dd - 2023-12-21 11:48:03 - wenijinew@gmail.com - v0.2.12 (tag: v0.2.12)
ff13168 - 2023-12-21 11:43:00 - wenijinew@gmail.com - Tune list.inactiveSelectionBackground which impacts Codeiu..
9c02714 - 2023-12-21 11:43:00 - wenijinew@gmail.com - Add yaml comment token color. Fix command center quickinpu..

## [v0.2.11] - 2023-12-20

0334d2f - 2023-12-20 22:03:57 - wenijinew@gmail.com - v0.2.11 (tag: v0.2.11)
2608d80 - 2023-12-20 21:57:53 - wenijinew@gmail.com - v0.2.11  
be7f72b - 2023-12-20 21:46:53 - wenijinew@gmail.com - Format code  
6970251 - 2023-12-20 21:46:53 - wenijinew@gmail.com - Fix testing.runAction  
d801c6e - 2023-12-20 20:49:46 - wenijinew@gmail.com - Fix diffEditor  
c0991bf - 2023-12-20 16:47:55 - wenijinew@gmail.com - Regenerate themes. Tune editorHoverWidget.background (tag: v0.2.10)

## [v0.2.10] - 2023-12-20

2acf0ff - 2023-12-20 16:40:04 - wenijinew@gmail.com - v0.2.10 - cleanup config.json. clean the logic to match co..
c7277d9 - 2023-12-20 16:40:04 - wenijinew@gmail.com - np

## [v0.2.9] - 2023-12-20

5bec678 - 2023-12-20 08:15:54 - wenijinew@gmail.com - v0.2.9: Generate all default themes. Tuning colors: defual.. (tag: v0.2.9)

## [v0.2.8] - 2023-12-19

eb916c7 - 2023-12-19 21:58:45 - wenijinew@gmail.com - v0.2.8 (tag: v0.2.8)
43f3535 - 2023-12-19 21:56:27 - wenijinew@gmail.com - Tuning colors. Remove unused groups in config.json.  
0fb7a79 - 2023-12-19 19:26:24 - wenijinew@gmail.com - Tuning colors: scrollbar, button, do not use 'token' when ..
0f4ac72 - 2023-12-19 18:31:33 - wenijinew@gmail.com - Tuning colors - separator, icon, syntax comment for erlang

## [v0.2.8] - 2023-12-19

462aee4 - 2023-12-19 07:19:39 - wenijinew@gmail.com - v0.2.7 - fix default themes issue (tag: v0.2.7)

## [v0.2.8] - 2023-12-19

5b82887 - 2023-12-19 06:19:08 - wenijinew@gmail.com - v0.2.6 - Applied peelee v0.2.1 solution for random base co.. (tag: v0.2.6)
87def52 - 2023-12-19 06:19:08 - wenijinew@gmail.com - v0.2.6

## [v0.2.8] - 2023-12-19

f029f08 - 2023-12-18 21:05:36 - wenijinew@gmail.com - v0.2.5 (tag: v0.2.5)
2f7f9d2 - 2023-12-18 16:18:24 - wenijinew@gmail.com - Good dark green theme. Hide borders of activitybar and tit..
96d0a34 - 2023-12-18 15:44:07 - wenijinew@gmail.com - Regenerate themes (tag: v0.2.4)

## [v0.2.8] - 2023-12-19

f093008 - 2023-12-18 15:41:32 - wenijinew@gmail.com - v0.2.4

## [v0.2.3] - 2023-12-18

bbaaf11 - 2023-12-18 14:53:23 - wenijinew@gmail.com - v0.2.3 (tag: v0.2.3)
74335ff - 2023-12-18 14:53:23 - wenijinew@gmail.com - Tuning tab background colors. scrollbarSlider, minimapSlid..
5c8321a - 2023-12-18 14:53:23 - wenijinew@gmail.com - Make tab active background darker  
5972ccd - 2023-12-18 14:53:23 - wenijinew@gmail.com - Regenerate several themes. Performs well.  
b2c59c1 - 2023-12-18 13:34:19 - wenijinew@gmail.com - Fix quick input background and foreground  
50554cb - 2023-12-18 11:32:58 - wenijinew@gmail.com - Fix inactive, disable foreground and background  
3994e2d - 2023-12-18 11:32:58 - wenijinew@gmail.com - Remove config for debug. It should be free to choose rando..
a3b0f93 - 2023-12-18 10:36:33 - wenijinew@gmail.com - Add CONTAINS in MatchRule  
e87d0e8 - 2023-12-18 10:36:33 - wenijinew@gmail.com - Fix wordHighlightStrongBorder to put it into ansiYellow gr..
31da91f - 2023-12-18 10:36:33 - wenijinew@gmail.com - Tune bg and fg of error and warning  
921df69 - 2023-12-18 10:36:33 - wenijinew@gmail.com - Merge status area to default area. Tune colors for editorO..
2699ed3 - 2023-12-18 10:36:33 - wenijinew@gmail.com - Remove old files. Tune color config.  
d7ac9c2 - 2023-12-18 10:36:33 - wenijinew@gmail.com - Use python to generate new theme file. Discard PowerShell ..
42224c5 - 2023-12-18 10:36:33 - wenijinew@gmail.com - Divide dark colors and light colors in all base colors. Us..
0e0acb1 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Fix editorSuggestWidget foreground colors. Divide foregrou.. (redesign)
f7821c5 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Fix editorSuggestWidget foreground  
ea3a539 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Fix focus foreground. Make it as light as possible  
eb0556e - 2023-12-17 22:38:04 - wenijinew@gmail.com - Fixed selection background. Configure it in status area  
50470d5 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Active foreground same color  
22cc4b1 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Set largest base range for default foreground. If set it a..
2952c72 - 2023-12-17 22:38:04 - wenijinew@gmail.com - tune dark yellow  
85bbf63 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Keep lineHighlightBackground, badge background, active for..
4585d16 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Configure color for unnecessary properties  
7ea6d0b - 2023-12-17 22:38:04 - wenijinew@gmail.com - Change BASIC, LIGHT, ALPHA for active, focus, and fold pro..
77a1f32 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Increate alpha value to make active property more light  
86e0bca - 2023-12-17 22:38:04 - wenijinew@gmail.com - Finished redesign  
55bc000 - 2023-12-17 22:38:04 - wenijinew@gmail.com - Redesign  
0cb3149 - 2023-12-17 22:38:04 - wenijinew@gmail.com - redesign dark violet theme  
b6a0225 - 2023-12-17 22:38:04 - wenijinew@gmail.com - redesign config json  
3fdec79 - 2023-12-17 22:38:04 - wenijinew@gmail.com - redesign  
1f3ac69 - 2023-12-16 08:36:13 - wenijinew@gmail.com - Use new solution for token colors - syntax highlight

## [v0.2.2] - 2023-12-15

452e6c9 - 2023-12-15 22:28:54 - wenijinew@gmail.com - v0.2.2 (tag: v0.2.2)
9d00497 - 2023-12-15 22:27:25 - wenijinew@gmail.com - Workable solution for all colors. To tune token colors for..
f9f935f - 2023-12-15 22:27:25 - wenijinew@gmail.com - 'basic' area should be treated in special way. it's not ov..
553a21b - 2023-12-15 22:27:25 - wenijinew@gmail.com - Fixed tab.activeBackground and breadcrumb.background. Make..
2ed1780 - 2023-12-15 19:53:04 - wenijinew@gmail.com - Use cache for basic group and prefix handled properties  
c942429 - 2023-12-15 19:53:04 - wenijinew@gmail.com - Tune tab background  
9ad418f - 2023-12-15 19:53:04 - wenijinew@gmail.com - Add cache for status property change  
9ce1ed7 - 2023-12-15 19:53:04 - wenijinew@gmail.com - Fixed status color areas settings  
a97b9a5 - 2023-12-15 19:53:04 - wenijinew@gmail.com - Fix color replacement bugs  
33462d4 - 2023-12-15 19:53:04 - wenijinew@gmail.com - Workable version to use JSON to configure all colors  
eccc1ea - 2023-12-15 19:53:04 - wenijinew@gmail.com - Configure the colors in json file.  
388083a - 2023-12-13 21:32:03 - wenijinew@gmail.com - Re-design the color configuration  
dcd5d2e - 2023-12-13 19:38:46 - wenijinew@gmail.com - Add function to printer colors in theme template and theme..
0312a25 - 2023-12-13 08:19:03 - wenijinew@gmail.com - Tunine the color strategy. Use min and max to control colo..
3af1be4 - 2023-12-13 08:16:54 - wenijinew@gmail.com - Tunine the color strategy. Use min and max to control colo..
5576044 - 2023-12-12 17:13:21 - wenijinew@gmail.com - Regenerate All Themes (tag: v0.2.1)
ce2366e - 2023-12-12 16:03:28 - wenijinew@gmail.com - Prepare v0.2.0 (tag: v0.2.0)
976cbe8 - 2023-12-12 16:01:10 - wenijinew@gmail.com - Regenerate dark blue theme. Tuned background colors of edi..
3f9b0a8 - 2023-12-12 15:35:30 - wenijinew@gmail.com - Refine the script and color configuration.

## [v0.1.9] - 2023-12-12

dd81db5 - 2023-12-12 13:11:22 - wenijinew@gmail.com - Prepare v0.1.9 (tag: v0.1.9)
be39f96 - 2023-12-12 13:09:50 - wenijinew@gmail.com - Fix color range issue caused by checking if the color rang..
1ac06cc - 2023-12-12 12:22:02 - wenijinew@gmail.com - Fixed the code issue about light color range level. Tuned ..
9cc8e33 - 2023-12-12 12:22:02 - wenijinew@gmail.com - Tuning all colors configuration in script  
a7b465e - 2023-12-12 12:22:02 - wenijinew@gmail.com - workable version to generate theme colors  
f738d4a - 2023-12-12 12:22:02 - wenijinew@gmail.com - Auto-generate the 'colors' for workbench properties  
8366a9b - 2023-12-11 14:05:52 - wenijinew@gmail.com - Re-generate all predefined themes (tag: v0.1.8)
6eb8360 - 2023-12-11 14:05:52 - wenijinew@gmail.com - Tune Colors, Re-generate Blue Theme

## [v0.1.8] - 2023-12-11

708c621 - 2023-12-11 14:05:52 - wenijinew@gmail.com - Prepare v0.1.8  
091a369 - 2023-12-11 13:04:32 - wenijinew@gmail.com - Apply dark color max 60. Use big fix from peelee  
72340b4 - 2023-12-11 13:04:32 - wenijinew@gmail.com - Fix editor word highlight  
7e5592c - 2023-12-11 13:04:32 - wenijinew@gmail.com - Fix bracket match  
60168f3 - 2023-12-11 13:04:32 - wenijinew@gmail.com - Fix terminal ansi colors  
792476f - 2023-12-11 10:52:33 - wenijinew@gmail.com - Fix notification  
7169be7 - 2023-12-11 10:52:33 - wenijinew@gmail.com - Fixed button background

## [v0.1.7] - 2023-12-11

42b9c98 - 2023-12-11 08:24:31 - wenijinew@gmail.com - v0.1.7 (tag: v0.1.7)
3b221be - 2023-12-11 07:48:23 - wenijinew@gmail.com - Use different gradational total for general color and dark..

## [v0.1.6] - 2023-12-10

1b7c360 - 2023-12-10 22:10:18 - wenijinew@gmail.com - v0.1.6 (tag: v0.1.6)
1bab04e - 2023-12-10 22:10:18 - wenijinew@gmail.com - Use predefined dark base colors for palette

## [v0.1.5] - 2023-12-09

28df6f6 - 2023-12-09 22:17:29 - wenijinew@gmail.com - Prepare v0.1.5 (tag: v0.1.5)
11f6725 - 2023-12-09 22:03:01 - wenijinew@gmail.com - Refine python script to update template file with random t..
6529940 - 2023-12-09 22:03:01 - wenijinew@gmail.com - Fix terminal colors  
7af37e0 - 2023-12-09 21:19:28 - wenijinew@gmail.com - Fix editor highlight word and text  
99ee1fd - 2023-12-09 21:19:28 - wenijinew@gmail.com - Fix editorIndentGuide  
d9f7442 - 2023-12-09 21:19:28 - wenijinew@gmail.com - Fix EditorGutter, DiffEditor  
d445ac1 - 2023-12-09 21:19:28 - wenijinew@gmail.com - Fix EditorGutter, DiffEditor  
1709418 - 2023-12-09 21:19:28 - wenijinew@gmail.com - Fix codelens hover foreground

## [v0.1.4] - 2023-12-09

f5ba751 - 2023-12-09 17:34:34 - wenijinew@gmail.com - Prepare for v0.1.4 (tag: v0.1.4)
b73ff49 - 2023-12-09 17:30:07 - wenijinew@gmail.com - Tune theme template. Applied final solution. Add python sc..
0396c40 - 2023-12-09 10:53:21 - wenijinew@gmail.com - Generate more lighter colors. Use bigger color range in th..
55f4de9 - 2023-12-09 10:53:21 - wenijinew@gmail.com - :Fix statusBar.noFolderBackground  
f873aef - 2023-12-09 08:15:18 - wenijinew@gmail.com - NP  
2793edb - 2023-12-09 08:15:18 - wenijinew@gmail.com - NP  
d2d57dd - 2023-12-08 18:13:08 - wenijinew@gmail.com - Tune variable color  
9be7599 - 2023-12-08 18:13:08 - wenijinew@gmail.com - Tune editorCodeLens, import, package  
4d0b57a - 2023-12-08 18:13:08 - wenijinew@gmail.com - Tune editor word highlight  
5520375 - 2023-12-08 18:13:08 - wenijinew@gmail.com - Add Dark Yellow Theme  
3463228 - 2023-12-07 21:49:02 - wenijinew@gmail.com - Add Dark Green Theme. Restore Error Color to #820000  
1b893fd - 2023-12-07 20:34:14 - wenijinew@gmail.com - Add new themes Dark Blue, Dark Cyan, Dark Lime (tag: v0.1.3)
8e39547 - 2023-12-07 20:34:14 - wenijinew@gmail.com - Add new themes: ViiV-Cyan-Pearl, ViiV-Olive-Gem, ViiV-Oliv..
29e1ead - 2023-12-07 20:34:14 - wenijinew@gmail.com - Tiny Change  
d1665bb - 2023-12-07 20:28:37 - wenijinew@gmail.com - Add new themes Dark Blue, Dark Cyan, Dark Lime (#9)  
98f5467 - 2023-12-07 19:52:31 - wenijinew@gmail.com - Add new themes: ViiV-Cyan-Pearl, ViiV-Olive-Gem, ViiV-Oliv.. (tag: v0.1.2)
ede4bf6 - 2023-12-07 19:47:26 - wenijinew@gmail.com - Create main.yml (#7)  
84e59fb - 2023-12-07 19:24:09 - wenijinew@gmail.com - Add new themes: ViiV-Cyan-Pearl, ViiV-Olive-Gem, ViiV-Oliv..
71e7ebe - 2023-12-06 21:45:01 - wenijinew@gmail.com - Tune auto theme script to generate dark colors  
0e49736 - 2023-12-06 20:13:08 - wenijinew@gmail.com - Add script to generate dynamic theme  
c7bf141 - 2023-12-06 12:48:17 - wenijinew@gmail.com - Add new theme ViiV-Black-Pearl (#5)  
665a3df - 2023-12-06 10:04:45 - wenijinew@gmail.com - Tune the bg fg color for list selection (#4)  
f8e0de9 - 2023-12-05 19:36:41 - wenijinew@gmail.com - Use unified red color (#3)  
149e7f5 - 2023-12-05 16:46:12 - wenijinew@gmail.com - Tuned colors of Codeium chat. (#2)  
0367c9c - 2023-12-04 09:22:22 - wenijinew@gmail.com - Tuning colors. (#1)  
0988748 - 2023-12-01 12:38:34 - wenijinew@gmail.com - Color change on settings view  
ed74510 - 2023-12-01 11:35:13 - wenijinew@gmail.com - Fix background color in keybinding table  
8578638 - 2023-11-30 21:45:43 - wenijinew@gmail.com - Little Change  
1d30c7f - 2023-11-30 21:35:04 - wenijinew@gmail.com - Add preview image. Logo. Big change for theme colors.  
828a4ec - 2023-11-24 11:22:50 - wenijinew@gmail.com - Rename to viiv

## [v0.0.2] - 2023-11-23

f4e6854 - 2023-11-23 15:15:54 - wenijinew@gmail.com - Prepare release 0.0.2  
5134dc1 - 2023-11-13 08:52:15 - wenijinew@gmail.com - Tuning C code comment color  
838c7aa - 2023-11-08 20:55:52 - wenijinew@gmail.com - Tuning error colors  
f707066 - 2023-11-04 09:12:39 - wenijinew@gmail.com - Tune theme  
35ab32e - 2023-10-30 21:52:56 - wenijinew@gmail.com - Modify diffEditor inserted background  
35619f1 - 2023-10-30 18:32:43 - wenijinew@gmail.com - Tunine activity badge color  
563af5b - 2023-10-25 21:43:59 - wenijinew@gmail.com - Tune theme color for terminal command decorations  
b1fea09 - 2023-10-19 09:27:03 - wenijinew@gmail.com - [FMP] Test Code - Tuning theme. Format  
9a67695 - 2023-10-19 08:02:04 - wenijinew@gmail.com - [FMP] Test Code - Tuning theme  
5716fe9 - 2023-10-17 11:49:47 - wenijinew@gmail.com - Tuning theme for pythno, markdown, workbenth  
b0de25a - 2023-10-16 16:46:01 - wenijinew@gmail.com - [Init] Tuning foreground color for menu, file explorer fil..
219e08f - 2023-10-16 14:53:24 - wenijinew@gmail.com - [Init] Create files

## Reference

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.
