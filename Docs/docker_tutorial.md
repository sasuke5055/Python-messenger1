# Jak odpalić serwer na dockerze
W celu odpalenia serwera na dockerze należy:
* Zainstalować docker
* Zainstalować docker-compose
* Dać im wszystkie uprawnienia jak każą w poradnikach (dość istotne)
* Wejść w folder python-project
* Wpisać 'docker-compose build'
* Ja się zbuilduje i pobierze wszystkie dependencies to należy wpisać
 'docker-compose up'
 
Jeśli będzie error z bazą danych to:
* Zabijamy nasz serwer (ctr+c na przykład)
* Puszczamy jeszcze raz, powinno już działać

Jeśli dalej nie będzie działać, to zabijmy naszą instancję mysql-servera, czasem gryzą się adresy
