// Fill out your copyright notice in the Description page of Project Settings.
//FLinearColor color(1, 1, 1);
//UKismetSystemLibrary::PrintString(GetWorld(),(FString)("xD"), true, false, color, 2);

#include "SpawnPolygonActor.h"

// Sets default values
ASpawnPolygonActor::ASpawnPolygonActor()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;
	mesh = CreateDefaultSubobject<UProceduralMeshComponent>("Procedural Mesh");
	// New in UE 4.17, multi-threaded PhysX cooking.
	mesh->bUseAsyncCooking = true;
	RootComponent = mesh;
}

// Called when the game starts or when spawned
void ASpawnPolygonActor::BeginPlay()
{
	Super::BeginPlay();
}

void ASpawnPolygonActor::PostLoad()
{
	Super::PostLoad();
}

void ASpawnPolygonActor::PostActorCreated()
{
	Super::PostActorCreated();
}

// Called every frame
void ASpawnPolygonActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void ASpawnPolygonActor::spawnPolygon()
{
	TArray<FVector> verticesTest;
	vertices.Add(FVector(0, 200, 0));
	vertices.Add(FVector(100, 200, 0));
	vertices.Add(FVector(0, 200, 100));
	vertices.Add(FVector(0, 100, 0));

	TArray<FVector2D> UV0Test;
	UV0.Add(FVector2D(0.5f, 1.0f));
	UV0.Add(FVector2D(1.0f, 1.0f));
	UV0.Add(FVector2D(0.5f, 0.0f));
	UV0.Add(FVector2D(0.0f, 1.0f));

	TArray<int32> TrianglesTest;
	TrianglesTest.Add(0);
	TrianglesTest.Add(1);
	TrianglesTest.Add(2);
	TrianglesTest.Add(0);
	TrianglesTest.Add(2);
	TrianglesTest.Add(3);


	TArray<FVector> normals;

	TArray<FProcMeshTangent> tangents;

	TArray<FLinearColor> vertexColors;


	mesh->CreateMeshSection_LinearColor(0, verticesTest, TrianglesTest, normals, UV0Test, vertexColors, tangents, true);

	// Enable collision data
	mesh->ContainsPhysicsTriMeshData(true);
}

void ASpawnPolygonActor::readFromFile(FString fileName)
{
	TArray<FString> stringsArray;
	TArray<FString, FDefaultAllocator> tmp;
	FString tmpValue1, tmpValue2, tmpValue3;
	FString deliminer = " ";
	FFileHelper::LoadANSITextFileToStrings(*fileName, NULL, stringsArray);
	for (int i = 0; i < stringsArray.Num(); i++) {
		stringsArray[i].ParseIntoArrayWS(tmp, *deliminer, true);
		if (tmp[0] == "v") {
			tmpValue1 = tmp[1];
			tmpValue2 = tmp[2];
			tmpValue3 = tmp[3];
			vertices.Add(FVector(FCString::Atof(*tmpValue1), FCString::Atof(*tmpValue2), FCString::Atof(*tmpValue3)));
		}
		else if (tmp[0] == "f") {
			tmpValue1 = tmp[1];
			tmpValue2 = tmp[2];
			tmpValue3 = tmp[3];
			triangles.Add(FCString::Atoi(*tmpValue1));
			triangles.Add(FCString::Atoi(*tmpValue2));
			triangles.Add(FCString::Atoi(*tmpValue3));
		}
		else if (tmp[0] == "u") {
			tmpValue1 = tmp[1];
			tmpValue2 = tmp[2];
			UV0.Add(FVector2D(FCString::Atof(*tmpValue1), FCString::Atof(*tmpValue2)));
		}
	}
}

void ASpawnPolygonActor::spawn()
{
	TArray<FVector> normals;
	TArray<FProcMeshTangent> tangents;
	TArray<FLinearColor> vertexColors;
	mesh->CreateMeshSection_LinearColor(0, vertices, triangles, normals, UV0, vertexColors, tangents, true);
}

void ASpawnPolygonActor::importFromFile() {
	readFromCOORDFile(100);
	readFromUFile(100);
	readFromELEMENTSFile();
	setTexture(path+"\\S.txt");
	spawn();
}

void ASpawnPolygonActor::addVertex(double x, double y, double z)
{
	vertices.Add(FVector(x, y, z));
}

void ASpawnPolygonActor::clearVerticesArray()
{
	vertices.Empty();
}

void ASpawnPolygonActor::addTriangle(int V1, int V2, int V3)
{
	triangles.Add(V1);
	triangles.Add(V2);
	triangles.Add(V3);
}

void ASpawnPolygonActor::clearTrianglesArray()
{
	triangles.Empty();
}

void ASpawnPolygonActor::addTexture(double UV)
{
	UV0.Add(FVector2D(UV, UV));
}

void ASpawnPolygonActor::clearTextureArray()
{
	UV0.Empty();
}

void ASpawnPolygonActor::addBlock(int V1, int V2, int V3, int V4, int V5, int V6, int V7, int V8)
{
	//LEFT SIDE
	addTriangle(V1, V2, V3);
	addTriangle(V1, V3, V4);
	//RIGHT SIDE
	addTriangle(V5, V7, V6);
	addTriangle(V5, V8, V7);
	//FRONT
	addTriangle(V1, V6, V2);
	addTriangle(V1, V5, V6);
	//TOP
	addTriangle(V4, V8, V5);
	addTriangle(V1, V4, V5);
	//BACK
	addTriangle(V4, V7, V8);
	addTriangle(V3, V7, V4);
	//BOTTOM
	addTriangle(V2, V6, V3);
	addTriangle(V3, V6, V7);
}

void ASpawnPolygonActor::addTetrahedron(int V1, int V2, int V3, int V4){
	addTriangle(V1, V2, V3);
	addTriangle(V2, V4, V3);
	addTriangle(V1, V4, V2);
	addTriangle(V1, V3, V4);
}

void ASpawnPolygonActor::add2D3Node(int V1, int V2, int V3)
{
	addTriangle(V1, V3, V2);
}

void ASpawnPolygonActor::add2D4Node(int V1, int V2, int V3, int V4)
{
	addTriangle(V1, V3, V2);
	addTriangle(V1, V4, V3);
}

void ASpawnPolygonActor::add2D6Node(int V1, int V2, int V3, int V4, int V5, int V6)
{
	addTriangle(V1, V6, V4);
	addTriangle(V4, V6, V5);
	addTriangle(V4, V5, V2);
	addTriangle(V6, V3, V5);
}

void ASpawnPolygonActor::readFromCOORDFile(float scale)
{
	scale /= 100.f;
	if (vertices.Num() > 0)
		clearVerticesArray();
	FString fileName = path + "\\model\\COORD.txt";
	TArray<FString> stringsArray;
	TArray<FString, FDefaultAllocator> tmp;
	FString deliminer = " ";
	FFileHelper::LoadANSITextFileToStrings(*fileName, NULL, stringsArray);
	FString::CullArray(&stringsArray);
	stringsArray[0].ParseIntoArrayWS(tmp, *deliminer, true);
	nodesCounter = stringsArray.Num();
	if (tmp.Num() == 3) {
		threeDimension = true;
		for (int i = 0; i < stringsArray.Num(); i++) {
			stringsArray[i].ParseIntoArrayWS(tmp, *deliminer, true);
			addVertex(FCString::Atof(*tmp[0]) * 100. * scale, FCString::Atof(*tmp[1]) * 100. * scale, FCString::Atof(*tmp[2]) * 100. * scale);
		}
	}
	else {
		threeDimension = false;
		for (int i = 0; i < stringsArray.Num(); i++) {
			stringsArray[i].ParseIntoArrayWS(tmp, *deliminer, true);
			addVertex(FCString::Atof(*tmp[0]) * 100. * scale, FCString::Atof(*tmp[1]) * 100. * scale, 0.0f);
		}
	}
}

void ASpawnPolygonActor::readFromELEMENTSFile()
{
	FString fileName = path + "\\model\\ELEMENTS.txt";
	TArray<FString> stringsArray;
	TArray<FString, FDefaultAllocator> tmp;
	FString deliminer = " ";
	FFileHelper::LoadANSITextFileToStrings(*fileName, NULL, stringsArray);
	FString::CullArray(&stringsArray);
	stringsArray[0].ParseIntoArrayWS(tmp, *deliminer, true);
	if(threeDimension)
		for (int i = 0; i < stringsArray.Num(); i++) {
			stringsArray[i].ParseIntoArrayWS(tmp, *deliminer, true);
			switch (tmp.Num()) {
			case 4:
				addTetrahedron(FCString::Atoi(*tmp[0]),
					FCString::Atoi(*tmp[1]),
					FCString::Atoi(*tmp[2]),
					FCString::Atoi(*tmp[3]));
				break;
			case 8:
				addBlock(FCString::Atoi(*tmp[0]),
					FCString::Atoi(*tmp[1]),
					FCString::Atoi(*tmp[2]),
					FCString::Atoi(*tmp[3]),
					FCString::Atoi(*tmp[4]),
					FCString::Atoi(*tmp[5]),
					FCString::Atoi(*tmp[6]),
					FCString::Atoi(*tmp[7]));
				break;
			}
		}
	else
		for (int i = 0; i < stringsArray.Num(); i++) {
			stringsArray[i].ParseIntoArrayWS(tmp, *deliminer, true);
			switch (tmp.Num()) {
			case 3:
				add2D3Node(FCString::Atoi(*tmp[0]),
					FCString::Atoi(*tmp[1]),
					FCString::Atoi(*tmp[2]));
				break;
			case 4:
				add2D4Node(FCString::Atoi(*tmp[0]),
					FCString::Atoi(*tmp[1]),
					FCString::Atoi(*tmp[2]),
					FCString::Atoi(*tmp[3]));
				break;
			case 6:
				add2D6Node(FCString::Atoi(*tmp[0]),
					FCString::Atoi(*tmp[1]),
					FCString::Atoi(*tmp[2]),
					FCString::Atoi(*tmp[3]),
					FCString::Atoi(*tmp[4]),
					FCString::Atoi(*tmp[5]));
				break;
			}
		}
}

void ASpawnPolygonActor::readFromUFile(float scale)
{
	scale /= 100.f;
	FString fileName1 = path + "\\model\\U1.txt";
	FString fileName2 = path + "\\model\\U2.txt";
	FString fileName3;
	if(threeDimension)
		fileName3 = path + "\\model\\U3.txt";
	FString fileName4 = path + "\\model\\scale_factor.txt";
	TArray<FString> stringsArray1;
	TArray<FString> stringsArray2;
	TArray<FString> stringsArray3;
	TArray<FString> stringsArray4;
	TArray<FString, FDefaultAllocator> tmp;
	FString tmpValue;
	FString deliminer = " ";
	FFileHelper::LoadANSITextFileToStrings(*fileName1, NULL, stringsArray1);
	FFileHelper::LoadANSITextFileToStrings(*fileName2, NULL, stringsArray2);
	if (threeDimension)
		FFileHelper::LoadANSITextFileToStrings(*fileName3, NULL, stringsArray3);
	FFileHelper::LoadANSITextFileToStrings(*fileName4, NULL, stringsArray4);
	FString::CullArray(&stringsArray1);
	FString::CullArray(&stringsArray2);
	if (threeDimension)
		FString::CullArray(&stringsArray3);
	FString::CullArray(&stringsArray4);
	stringsArray4[0].ParseIntoArrayWS(tmp, *deliminer, true);
	tmpValue = tmp[0];
	double scaleFactor = FCString::Atof(*tmpValue);
	for (int i = 0; i < stringsArray1.Num(); i++) {
		stringsArray1[i].ParseIntoArrayWS(tmp, *deliminer, true);
		tmpValue = tmp[0];
		vertices[i][0] += (FCString::Atof(*tmpValue) * scaleFactor * 100. * scale);
		stringsArray2[i].ParseIntoArrayWS(tmp, *deliminer, true);
		tmpValue = tmp[0];
		vertices[i][1] += (FCString::Atof(*tmpValue) * scaleFactor * 100. * scale);
		if (threeDimension) {
			stringsArray3[i].ParseIntoArrayWS(tmp, *deliminer, true);
			tmpValue = tmp[0];
			vertices[i][2] += (FCString::Atof(*tmpValue) * scaleFactor * 100. * scale);
		}
	}
}

void ASpawnPolygonActor::setTexture(FString fileName)
{
	float min, max;
	double tmpUV0;
	TArray<int> counterArray;
	if (UV0.Num() > 0)
		clearTextureArray();
	for (int i = 0; i < vertices.Num(); i++) {
		addTexture(0.);
		counterArray.Add(0);
	}
	TArray<FString> stringsArray1;
	TArray<FString> stringsArray2;
	TArray<FString, FDefaultAllocator> tmp;
	FString deliminer = " ";
	FString elementsFileName = path + "\\model\\ELEMENTS.txt";
	FFileHelper::LoadANSITextFileToStrings(*fileName, NULL, stringsArray1);
	FFileHelper::LoadANSITextFileToStrings(*elementsFileName, NULL, stringsArray2);
	FString::CullArray(&stringsArray1);
	FString::CullArray(&stringsArray2);
	min = FCString::Atof(*stringsArray1[0]);
	max = FCString::Atof(*stringsArray1[0]);
	double tmpNodeValue[20];
	if (stringsArray1.Num() != nodesCounter) {
		if(!threeDimension){
			for (int i = 0; i < stringsArray2.Num(); i++) {
				stringsArray2[i].ParseIntoArrayWS(tmp, *deliminer, true);
				switch (tmp.Num()) {
				case 3:
					if (FCString::Atof(*stringsArray1[i]) < min)
						min = FCString::Atof(*stringsArray1[i]);
					if (FCString::Atof(*stringsArray1[i]) > max)
						max = FCString::Atof(*stringsArray1[i]);
					counterArray[FCString::Atoi(*tmp[0])] += 1;
					counterArray[FCString::Atoi(*tmp[1])] += 1;
					counterArray[FCString::Atoi(*tmp[2])] += 1;
					UV0[FCString::Atoi(*tmp[0])][0] += FCString::Atof(*stringsArray1[i]);
					UV0[FCString::Atoi(*tmp[1])][0] += FCString::Atof(*stringsArray1[i]);
					UV0[FCString::Atoi(*tmp[2])][0] += FCString::Atof(*stringsArray1[i]);
					break;
				case 4:
					if (FCString::Atof(*stringsArray1[i]) < min)
						min = FCString::Atof(*stringsArray1[i]);
					if (FCString::Atof(*stringsArray1[i]) > max)
						max = FCString::Atof(*stringsArray1[i]);
					counterArray[FCString::Atoi(*tmp[0])] += 1;
					counterArray[FCString::Atoi(*tmp[1])] += 1;
					counterArray[FCString::Atoi(*tmp[2])] += 1;
					counterArray[FCString::Atoi(*tmp[3])] += 1;
					UV0[FCString::Atoi(*tmp[0])][0] += FCString::Atof(*stringsArray1[i]);
					UV0[FCString::Atoi(*tmp[1])][0] += FCString::Atof(*stringsArray1[i]);
					UV0[FCString::Atoi(*tmp[2])][0] += FCString::Atof(*stringsArray1[i]);
					UV0[FCString::Atoi(*tmp[3])][0] += FCString::Atof(*stringsArray1[i]);
					break;
				case 6:
					tmpNodeValue[0] = 0;
					tmpNodeValue[1] = 0;
					tmpNodeValue[2] = 0;
					tmpNodeValue[3] = 0;
					tmpNodeValue[4] = 0;
					tmpNodeValue[5] = 0;
					counterArray[FCString::Atoi(*tmp[0])] += 1;
					counterArray[FCString::Atoi(*tmp[1])] += 1;
					counterArray[FCString::Atoi(*tmp[2])] += 1;
					counterArray[FCString::Atoi(*tmp[3])] += 1;
					counterArray[FCString::Atoi(*tmp[4])] += 1;
					counterArray[FCString::Atoi(*tmp[5])] += 1;
					for (int ii = i * 3; ii < ((i * 3) + 3); ii++) {
						tmpNodeValue[0] += FCString::Atof(*stringsArray1[ii]);
						tmpNodeValue[1] += FCString::Atof(*stringsArray1[ii]);
						tmpNodeValue[2] += FCString::Atof(*stringsArray1[ii]);
						tmpNodeValue[3] += FCString::Atof(*stringsArray1[ii]);
						tmpNodeValue[4] += FCString::Atof(*stringsArray1[ii]);
						tmpNodeValue[5] += FCString::Atof(*stringsArray1[ii]);
					}
					tmpNodeValue[0] /= 3.;
					tmpNodeValue[1] /= 3.;
					tmpNodeValue[2] /= 3.;
					tmpNodeValue[3] /= 3.;
					tmpNodeValue[4] /= 3.;
					tmpNodeValue[5] /= 3.;
					for (int ii = 0; ii < 6; ii++) {
						if (tmpNodeValue[ii] < min)
							min = tmpNodeValue[ii];
						if (tmpNodeValue[ii] > max)
							max = tmpNodeValue[ii];
					}
					UV0[FCString::Atoi(*tmp[0])][0] += tmpNodeValue[0];
					UV0[FCString::Atoi(*tmp[1])][0] += tmpNodeValue[1];
					UV0[FCString::Atoi(*tmp[2])][0] += tmpNodeValue[2];
					UV0[FCString::Atoi(*tmp[3])][0] += tmpNodeValue[3];
					UV0[FCString::Atoi(*tmp[4])][0] += tmpNodeValue[4];
					UV0[FCString::Atoi(*tmp[5])][0] += tmpNodeValue[5];
				}
			}
		}
		else {

		}
		for (int i = 0; i < UV0.Num(); i++) {
			UV0[i][0] /= (float)counterArray[i];
		}
		for (int i = 0; i < UV0.Num(); i++) {
			tmpUV0 = setTextureCoordinates(min, max, UV0[i][0]);
			if (tmpUV0 <= 0.02)
				tmpUV0 = 0.03;
			if (tmpUV0 >= 0.98)
				tmpUV0 = 0.97;
			UV0[i][0] = tmpUV0;
			UV0[i][1] = tmpUV0;
		}
	}
	else {
		for (int i = 1; i < stringsArray1.Num(); i++) {
			if (FCString::Atof(*stringsArray1[i]) < min)
				min = FCString::Atof(*stringsArray1[i]);
			if (FCString::Atof(*stringsArray1[i]) > max)
				max = FCString::Atof(*stringsArray1[i]);
		}
		for (int i = 0; i < stringsArray1.Num(); i++) {
			tmpUV0 = setTextureCoordinates(min, max, FCString::Atof(*stringsArray1[i]));
			if (tmpUV0 <= 0.02)
				tmpUV0 = 0.03;
			if (tmpUV0 >= 0.98)
				tmpUV0 = 0.97;
			UV0[i][0] = tmpUV0;
			UV0[i][1] = tmpUV0;
		}
	}
	globalMin = min;
	globalMax = max;
}

double ASpawnPolygonActor::setTextureCoordinates(double min, double max, double value)
{
	return (value - min) / (max - min);
}

void ASpawnPolygonActor::pickFolderButton(FString tmp)
{
	path = tmp;
}

void ASpawnPolygonActor::pickValueButton(FString name1, FString name2)
{
	setTexture(path + "\\" + name1 + "\\" + name2 + ".txt");
}

void ASpawnPolygonActor::readModelButton(float scale)
{
	readFromCOORDFile(scale);
	readFromUFile(scale);
	readFromELEMENTSFile();
}

void ASpawnPolygonActor::rendButton()
{
	spawn();
	mesh->SetMaterial(0, material);
}

void ASpawnPolygonActor::clearButton()
{
	clearTextureArray();
	clearVerticesArray();
	clearTrianglesArray();
	path = "";
	spawn();
}

void ASpawnPolygonActor::coordinatesOfModel(float& x1, float& x2, float& y1, float& y2, float& z1, float& z2)
{
	x1 = vertices[0][0];
	x2 = vertices[0][0];

	y1 = vertices[0][1];
	y2 = vertices[0][1];

	z1 = vertices[0][2];
	z2 = vertices[0][2];
	for (int i = 0; i < vertices.Num(); i++) {
		if (vertices[i][0] < x1)
			x1 = vertices[i][0];
		if (vertices[i][0] > x2)
			x2 = vertices[i][0];
		if (vertices[i][1] < y1)
			y1 = vertices[i][1];
		if (vertices[i][1] > y2)
			y2 = vertices[i][1];
		if (vertices[i][2] < z1)
			z1 = vertices[i][2];
		if (vertices[i][2] > z2)
			z2 = vertices[i][2];
	}
}

void ASpawnPolygonActor::minMaxValues(float& min, float& max)
{
	min = globalMin;
	max = globalMax;
}
