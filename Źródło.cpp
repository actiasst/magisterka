#include <iostream>
#include <fstream>

using namespace std;

fstream plik("D:\\object.txt", ios::out);

void dodaj_wierzcholki();
void dodaj_wierzcholek(double, double, double);
void dodaj_bryle(int, int, int, int, int, int, int, int);
void dodaj_trojkat(int, int, int);
void dodaj_teksture(double);
void dodaj_tekstury();

int main() {
	dodaj_wierzcholki();
	dodaj_tekstury();
	dodaj_bryle(0, 1, 2, 3, 4, 5, 6, 7);
	//dodaj_bryle(4, 5, 6, 7, 8, 9, 10, 11);

	plik.close();
	system("pause");
}

void dodaj_wierzcholki() {
	dodaj_wierzcholek(0, 0, 100);
	dodaj_wierzcholek(0, 0, 0);
	dodaj_wierzcholek(100, 0, 0);
	dodaj_wierzcholek(100, 0, 100);
	dodaj_wierzcholek(0, 100, 100);
	dodaj_wierzcholek(0, 100, 0);
	dodaj_wierzcholek(100, 100, 0);
	dodaj_wierzcholek(100, 100, 100);
	dodaj_wierzcholek(-100, 200, 200);
	dodaj_wierzcholek(-100, 200, 0);
	dodaj_wierzcholek(200, 200, 0);
	dodaj_wierzcholek(200, 200, 200);
}

void dodaj_wierzcholek(double x, double y, double z) {
	plik << "v " << x << " " << y << " " << z << endl;
}

void dodaj_bryle(int v1, int v2, int v3, int v4, int v5, int v6, int v7, int v8) {
	//LEWY
	dodaj_trojkat(v1, v3, v2);
	dodaj_trojkat(v1, v4, v3);
	//PRAWY
	dodaj_trojkat(v5, v6, v7);
	dodaj_trojkat(v5, v7, v8);
	//PRZOD
	dodaj_trojkat(v1, v2, v6);
	dodaj_trojkat(v1, v6, v5);
	//GORA
	dodaj_trojkat(v4, v5, v8);
	dodaj_trojkat(v1, v5, v4);
	//TYL
	dodaj_trojkat(v4, v8, v7);
	dodaj_trojkat(v3, v4, v7);
	//DOL
	dodaj_trojkat(v2, v3, v6);
	dodaj_trojkat(v3, v7, v6);
}

void dodaj_trojkat(int v1, int v2, int v3) {
	plik << "f " << v1 << " " << v2 << " " << v3 << endl;
}

void dodaj_tekstury() {
	dodaj_teksture(0);
	dodaj_teksture(0.3);
	dodaj_teksture(0.4);
	dodaj_teksture(1);
	dodaj_teksture(0);
	dodaj_teksture(0.3);
	dodaj_teksture(0.4);
	dodaj_teksture(1);
}

void dodaj_teksture(double x) {
	plik << "u " << x << " " << x << endl;
}