$acrName = "crprizio"
$imageName = "scraper-pqm"
$tag = "latest"
$loginServer = az acr show --name $acrName --query loginServer --output tsv

Write-Host "`n Iniciando sesion en Azure..."
az login
az acr login --name $acrName

Write-Host "`n Construyendo imagen..."
docker build -t "${loginServer}/${imageName}:${tag}" .


Write-Host "`n Subiendo imagen a ACR..."
docker push "${loginServer}/${imageName}:${tag}"

Write-Host "`n Imagen publicada en: ${loginServer}/${imageName}:${tag}"