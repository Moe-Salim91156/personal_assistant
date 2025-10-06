#!/bin/bash


WORK_DIR="$HOME/$1"
REPO_DIR="$HOME/$2"

PROJECTS=($(ls -d "$WORK_DIR"/*/))

if [[ ${#PROJECTS[@]} -eq 0 ]]; then
    echo "No projects found in $WORK_DIR."
    exit 1
fi

echo "Select a project to copy and push:"
select PROJECT_PATH in "${PROJECTS[@]}"; do
	if [[ -n "$PROJECT_PATH" ]]; then
		PROJECT_DIR=$(basename "$PROJECT_PATH")
		echo "You selected: $PROJECT_DIR"
		break
	else
		echo "Invalid selection. Please try again."
	fi
done

cp -r "$PROJECT_PATH" "$REPO_DIR"

cd "$REPO_DIR/$PROJECT_DIR" || exit 1

if [[ -d ".git" ]]; then
    rm -rf .git
    echo ".git directory removed."
fi


read -p "Push? (y/n) : " option

if [ $option == y ]; then
	exec push # executing the push script
else
	echo "Project $PROJECT_DIR has been successfully pushed to the repository."
fi

