param(
    [Parameter(Mandatory = $true)]
    [string]$Root,
    [Parameter(Mandatory = $true)]
    [ValidateSet('Qualification', 'Training')]
    [string]$Phase,
    [Parameter(Mandatory = $true)]
    [string]$LeaseId,
    [Parameter(Mandatory = $true)]
    [string]$HostBootId
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Experiment = Join-Path $Root 'input/training-experiment.json'
$Corpus = Join-Path $Root 'input/corpus.json'
$Trainer = Join-Path $Root 'input/caplab_qwen27b_qlora_r2.py'
$R1Trainer = Join-Path $Root 'input/caplab_qwen27b_qlora.py'
$SharedEnvironment = 'C:/Users/halbr/caplab/experiments/caplab-review-dissent-qwen27b-qlora-r1/.venv'
$Model = 'C:/Users/halbr/caplab/models/Qwen3.6-27B-6a9e13bd6fc8f0983b9b99948120bc37f49c13e9'
$QualificationOutput = Join-Path $Root 'qualification-output'
$TrainingOutput = Join-Path $Root 'training-output'
$QualificationAcceptance = Join-Path $Root 'qualification-accepted.json'

function Assert-Sha256 {
    param([string]$Path, [string]$Expected)
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected) {
        throw "sha256 mismatch: $Path expected=$Expected actual=$Actual"
    }
}

Assert-Sha256 $Experiment '4f8d4f0792cbb56aeee3c00e0de3c43fe4efc7f13c2316860801ffd547febfe0'
Assert-Sha256 $Corpus '09ec666630189ebbe9bf180d3dd567623f8dbee753871f63ac7f66c712cb87f2'
Assert-Sha256 $Trainer '4f1adb2d654a210fbf11db9ac39a9e58f2e288dd3d9ea75ea0923b410a1e9ae6'
Assert-Sha256 $R1Trainer '5a2c7397ebc740ee1970045cd105557145281d9f880309994e566208038303c8'
Assert-Sha256 (Join-Path $Root 'input/training_supervisor.py') '548897358b4c769992b2ce5b5056d13c3dc640f9dd0d86a3036083c7ba8fe0e9'
Assert-Sha256 (Join-Path $Model 'model.safetensors.index.json') 'a8ad2c26fb707ff8c245806315b03e3b4b74595528492423af5dae0ce39b4d9b'

$Python = Join-Path $SharedEnvironment 'Scripts/python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "frozen shared Python environment missing: $Python"
}

$Gpu = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
if ($Gpu.Trim() -ne 'NVIDIA GeForce RTX 3090 Ti, 24564') {
    throw "GPU binding mismatch: $Gpu"
}
$OperatingSystem = Get-CimInstance Win32_OperatingSystem
$CurrentBootId = $OperatingSystem.LastBootUpTime.ToUniversalTime().ToString('o')
if ($CurrentBootId -ne $HostBootId) {
    throw "host boot identity mismatch: expected=$HostBootId actual=$CurrentBootId"
}

ollama stop qwen3.6:27b

if ($Phase -eq 'Qualification') {
    if (Test-Path -LiteralPath $QualificationOutput) {
        throw "qualification output already exists: $QualificationOutput"
    }
    & $Python $Trainer `
        --mode qualify `
        --experiment $Experiment `
        --corpus $Corpus `
        --model-dir $Model `
        --output $QualificationOutput
} else {
    if (-not (Test-Path -LiteralPath $QualificationAcceptance -PathType Leaf)) {
        throw "qualification acceptance missing: $QualificationAcceptance"
    }
    $Acceptance = Get-Content -Raw -LiteralPath $QualificationAcceptance | ConvertFrom-Json
    if ($Acceptance.schema -ne 'caplab.training.host-qualification-acceptance/v1' `
        -or $Acceptance.experiment_id -ne 'caplab-review-dissent-qwen27b-qlora-r2' `
        -or $Acceptance.lease_id -ne $LeaseId `
        -or $Acceptance.host_boot_id -ne $HostBootId `
        -or $Acceptance.distinct_fleet_heartbeats -lt 4) {
        throw 'qualification acceptance contract mismatch'
    }
    Assert-Sha256 (Join-Path $QualificationOutput 'qualification.json') $Acceptance.qualification_sha256
    if (Test-Path -LiteralPath $TrainingOutput) {
        throw "training output already exists: $TrainingOutput"
    }
    & $Python $Trainer `
        --mode train `
        --experiment $Experiment `
        --corpus $Corpus `
        --model-dir $Model `
        --output $TrainingOutput
}

if ($LASTEXITCODE -ne 0) {
    throw "$Phase command failed with exit $LASTEXITCODE"
}

if ($Phase -eq 'Training') {
    if (-not (Test-Path -LiteralPath (Join-Path $TrainingOutput 'result.json') -PathType Leaf) `
        -or -not (Test-Path -LiteralPath (Join-Path $TrainingOutput 'final-adapter/adapter_model.safetensors') -PathType Leaf)) {
        throw 'training completed without a sealed final adapter and result'
    }
}
