$acrName = "acrprizio" #prd: "crprizio" | dev: "acrprizio"
$imageName = "scraper-wm"
$tag = "V1.0.1"
$loginServer = az acr show --name $acrName --query loginServer --output tsv

Write-Host "`n Iniciando sesion en Azure..."
az login
az acr login --name $acrName

Write-Host "`n Construyendo imagen..."
docker build -t "${loginServer}/${imageName}:${tag}" .


Write-Host "`n Subiendo imagen a ACR..."
docker push "${loginServer}/${imageName}:${tag}"

Write-Host "`n Imagen publicada en: ${loginServer}/${imageName}:${tag}"
