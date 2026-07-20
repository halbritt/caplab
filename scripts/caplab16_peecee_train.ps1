param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Experiment = Join-Path $Root 'input/training-experiment.json'
$Corpus = Join-Path $Root 'input/corpus.json'
$Trainer = Join-Path $Root 'input/caplab_qwen27b_qlora.py'
$Environment = Join-Path $Root '.venv'
$Model = 'C:/Users/halbr/caplab/models/Qwen3.6-27B-6a9e13bd6fc8f0983b9b99948120bc37f49c13e9'
$Output = Join-Path $Root 'training-output'

function Assert-Sha256 {
    param([string]$Path, [string]$Expected)
    $Actual = (Get-FileHash -Algorithm SHA256 $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected) {
        throw "sha256 mismatch: $Path expected=$Expected actual=$Actual"
    }
}

Assert-Sha256 $Experiment '56a997d3f8e5ed72db6e586b129356d2b4fef743d16e7eae243d4085e6cfbab6'
Assert-Sha256 $Corpus '09ec666630189ebbe9bf180d3dd567623f8dbee753871f63ac7f66c712cb87f2'
Assert-Sha256 $Trainer '5a2c7397ebc740ee1970045cd105557145281d9f880309994e566208038303c8'

if (Test-Path $Output) {
    throw "training output already exists: $Output"
}

$Gpu = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
if ($Gpu.Trim() -ne 'NVIDIA GeForce RTX 3090 Ti, 24564') {
    throw "GPU binding mismatch: $Gpu"
}

ollama stop qwen3.6:27b

if (-not (Test-Path (Join-Path $Environment 'Scripts/python.exe'))) {
    uv venv --python 3.12 --seed $Environment
}
$Python = Join-Path $Environment 'Scripts/python.exe'

uv pip install --python $Python --index https://download.pytorch.org/whl/cu130 'torch==2.12.1'
uv pip install --python $Python `
    'transformers==5.14.1' `
    'peft==0.19.1' `
    'trl==1.8.0' `
    'bitsandbytes==0.49.2' `
    'accelerate==1.14.0'

if (-not (Test-Path (Join-Path $Model 'model.safetensors.index.json'))) {
    New-Item -ItemType Directory -Force (Split-Path $Model) | Out-Null
    & (Join-Path $Environment 'Scripts/hf.exe') download `
        Qwen/Qwen3.6-27B `
        --revision 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 `
        --local-dir $Model
}

Assert-Sha256 (Join-Path $Model 'model.safetensors.index.json') 'a8ad2c26fb707ff8c245806315b03e3b4b74595528492423af5dae0ce39b4d9b'

& $Python $Trainer `
    --mode train `
    --experiment $Experiment `
    --corpus $Corpus `
    --model-dir $Model `
    --output $Output

if ($LASTEXITCODE -ne 0) {
    throw "training command failed with exit $LASTEXITCODE"
}
