# Versioned Save for Blender

Versioned Save is a lightweight Blender add-on that replaces the standard "Overwrite" behavior of Ctrl + S with an incremental saving system. Instead of overwriting your current file, it creates a new version (e.g., _v001, _v002), ensuring you never lose previous iterations of your work

## How It Works
When you press **Ctrl + S**:
* **If Enabled**: The script calculates the next version number based on existing files in your directory.
* **Naming Convention**: It renames the file from `project.blend` to `project_v001.blend`.

> **Important**: It is highly recommended to create a dedicated folder for each project to keep your versions organized.

## Installation
1. Download the [latest release](https://github.com/Felcon8/VersionedSaveAdd-on/releases)
2. Open Blender and go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded script.
4. Enable the checkbox for **Versioned Save**.

## Requirements
* Blender 3.0.0 or newer.
