# Fetch the exact four FLORES devtest mirror files used in this submission.
# Run from repository root; verify SHA-256 after download.
$ErrorActionPreference = 'Stop'
$out = Join-Path $PSScriptRoot 'corpus'
New-Item -ItemType Directory -Force $out | Out-Null
$base = 'https://raw.githubusercontent.com/AI4Bharat/CTQScorer/master/dataset/test'
$files = @{
  'eng_Latn.devtest' = '612e9fbe87997617c0fa8fa8929654a4f49b728d96738112c2b86ef6a1d78d88'
  'hin_Deva.devtest' = '5f5fd39acadca29fb044a0398e81869e48f37de979df086f2fad4a7d1fd2d015'
  'kan_Knda.devtest' = '58e8ed5ef79cfd9994e7d4010d22b5ce72c3559f0c8e988fbde11fa58a720cd8'
  'tam_Taml.devtest' = 'a18b26bf278e458f085c70173d6789d6108cb2e3346c81a1bd0f8aceb4ea30e4'
}
foreach ($item in $files.GetEnumerator()) {
  $target = Join-Path $out $item.Key
  Invoke-WebRequest -Uri "$base/$($item.Key)" -OutFile $target
  $actual = (Get-FileHash -Algorithm SHA256 $target).Hash.ToLowerInvariant()
  if ($actual -ne $item.Value) { throw "checksum mismatch for $($item.Key): $actual" }
}
Write-Output 'Downloaded 4 line-aligned files, 1012 lines each, with verified SHA-256.'
