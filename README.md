# Versioned Save for Blender

This add-on replaces the default `Ctrl + S` behavior with an incremental saving system.

## How It Works
When you press **Ctrl + S**:
* **If Enabled**: The script calculates the next version number based on existing files in your directory.
* **Naming Convention**: It renames the file from `project.blend` to `project_v001.blend`.

> **Important**: It is highly recommended to create a dedicated folder for each project to keep your versions organized.

## Installation
1. Download the [latest release](https://github.com/Felcon8/VersionedSaveAdd-on/releases)
2. Open Blender and go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded script.
4. Enable the checkbox for **System: Save New Version on Ctrl+S**.

## Requirements
* Blender 3.0.0 or newer.
