#!/bin/bash

TARGET_DIR="${1:-$HOME}"
echo "REMOVING ~/.cache folder"

if [ -z "$TARGET_DIR" ]; then
  echo "Usage: $0 /path/to/folder"
  exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: $TARGET_DIR is not a directory."
  exit 1
fi

cd "$TARGET_DIR" || exit

echo "📁 Cleaning cache folders in subdirectories..."

for folder in */ ; do
  [ -d "$folder" ] || continue

  cache_dir="${folder}cache"
  cache_dot_dir="${folder}.cache"

  if [ -d "$cache_dir" ]; then
    echo "🗑️  Removing cache: $cache_dir"
    rm -rf "$cache_dir"
  elif [ -d "$cache_dot_dir" ]; then
    echo "🗑️  Removing cache: $cache_dot_dir"
    rm -rf "$cache_dot_dir"
  else
    echo "ℹ️  No cache folder in $folder"
  fi
done



##############################################
# code below is done using GPT
# FOR .zwc files zcomp
#############################################

echo ""
echo "🧹 Cleaning .zcompdump* files..."

# List all .zcompdump* files sorted by newest first
files=($(ls -t .zcompdump* 2>/dev/null))

if [ "${#files[@]}" -gt 1 ]; then
  echo "Keeping: ${files[0]}"
  files=("${files[@]:1}")  # exclude the newest
  for file in "${files[@]}"; do
    echo "🗑️  Removing $file"
    rm -f "$file"
  done
else
  echo "Nothing to clean or only one .zcompdump file exists."
fi
echo ""
echo "✅ Done."

