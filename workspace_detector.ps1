# Common project indicators
$PROJECT_INDICATORS = @{
    "Node.js" = @("package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json")
    "Python" = @("requirements.txt", "pyproject.toml", "setup.py")
    "Rust" = @("Cargo.toml")
    "Go" = @("go.mod")
    "PHP" = @("composer.json")
    "Ruby" = @("Gemfile")
    "Java" = @("pom.xml", "build.gradle")
    "Static Website" = @("index.html", "index.htm")
    "Git Repository" = @(".git")
}

# Current working directory
$CURRENT_DIR = Get-Location

# Detect workspace
$workspace_path = $CURRENT_DIR.Path

# Check if the directory is a Git repository
function Is-GitRepo {
    param (
        [string]$path
    )
    if (Test-Path -Path (Join-Path $path ".git")) {
        return $true
    } else {
        return $false
    }
}

# Detect project type
function Detect-ProjectType {
    param (
        [string]$path
    )
    $files = Get-ChildItem -Path $path -File | Select-Object -ExpandProperty Name
    $project_type = "Generic Project"
    
    # Check for Git repository
    if (Is-GitRepo -path $path) {
        $project_type = "Git Repository"
    }
    
    # Check for project-specific files
    foreach ($project in $PROJECT_INDICATORS.Keys) {
        if ($project -eq "Git Repository") {
            continue  # Already checked
        }
        foreach ($indicator in $PROJECT_INDICATORS[$project]) {
            if ($files -contains $indicator) {
                $project_type = $project
                break
            }
        }
        if ($project_type -ne "Generic Project") {
            break
        }
    }
    
    # Check for static website
    if ($files -contains "index.html" -or $files -contains "index.htm") {
        if ($project_type -eq "Generic Project") {
            $project_type = "Static Website"
        }
    }
    
    return $project_type
}

# Get package manager
function Get-PackageManager {
    param (
        [string]$path
    )
    $files = Get-ChildItem -Path $path -File | Select-Object -ExpandProperty Name
    if ($files -contains "package.json") {
        return "npm"
    } elseif ($files -contains "yarn.lock") {
        return "yarn"
    } elseif ($files -contains "pnpm-lock.yaml") {
        return "pnpm"
    } else {
        return "None"
    }
}

# Main detection logic
function Detect-Workspace {
    $workspace_info = @{
        "workspace_path" = $workspace_path
        "project_type" = Detect-ProjectType -path $workspace_path
        "is_git_repo" = Is-GitRepo -path $workspace_path
        "package_manager" = Get-PackageManager -path $workspace_path
    }
    return $workspace_info
}

# Main script execution
$workspace_info = Detect-Workspace
Write-Output "Workspace: $($workspace_info.workspace_path)"
Write-Output "Project Type: $($workspace_info.project_type)"
Write-Output "Git: $(if ($workspace_info.is_git_repo) { "available" } else { "unavailable" })"
Write-Output "Package Manager: $($workspace_info.package_manager)"