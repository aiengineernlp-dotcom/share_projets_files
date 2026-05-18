star_wars = [125, 1977, 11000000]
raiders = [115, 1981, 18000000]
mean_girls = [97, 2004, 17000000]

def distance(movie1, movie2):
    squared_diff = 0
    for i in range(len(movie1)):
        squared_diff+= (movie1[i] - movie2[i])**2
        distance = squared_diff ** 0.5
        print(len(movie1))

        return distance


print(distance(star_wars,raiders))
print(distance(star_wars,mean_girls))






# 1.
# Modify your distance function to work with any number of dimensions. Use a for loop to iterate through the dimensions of each movie.
#
# Return the total distance between the two movies.
#
# Checkpoint 2 Step instruction is unavailable until previous steps are completed
# 2.
# We’ve added a third dimension to each of our movies.
#
# Print the new distance between Star Wars and Raiders of the Lost Ark.
#
# Print the new distance between Star Wars and Mean Girls.
#
# Which movie is Star Wars closer to now?





# Connexion
Connect-PnPOnline -Url "https://votreTenant-admin.sharepoint.com" -Interactive

# Email de l’utilisateur
$userLogin = "ali@votredomaine.com"

# Récupère tous les sites SharePoint
$sites = Get-PnPTenantSite

foreach ($site in $sites) {
    Write-Host "Nettoyage du site : $($site.Url)" -ForegroundColor Cyan
    Connect-PnPOnline -Url $site.Url -Interactive
    Remove-PnPUser -LoginName $userLogin -Force -ErrorAction SilentlyContinue
}