// Fill out your copyright notice in the Description page of Project Settings.


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
	/*FLinearColor color(0, 0, 0);
	UKismetSystemLibrary::PrintString(GetWorld(),(FString)("xD"), true, false, color, 2);*/
	//spawnPolygon();
}

void ASpawnPolygonActor::PostLoad()
{
	Super::PostLoad();
	/*FString fileName = "D:\\object.txt";
	readFromFile(fileName);
	spawn();*/
	importFromFile();
}

void ASpawnPolygonActor::PostActorCreated()
{
	Super::PostActorCreated();
	/*FString fileName = "D:\\object.txt";
	readFromFile(fileName);
	spawn();*/
	importFromFile();
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
	readFromCOORDFile();
	readFromUFile();
	readFromELEMENTSFile();
	setTexture("D:\\exported\\S.txt");
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

void ASpawnPolygonActor::readFromCOORDFile()
{
	FString fileName = "D:\\exported\\COORD.txt";
	TArray<FString> stringsArray;
	TArray<FString, FDefaultAllocator> tmp;
	FString deliminer = " ";
	FFileHelper::LoadANSITextFileToStrings(*fileName, NULL, stringsArray);
	FString::CullArray(&stringsArray);
	for (int i = 0; i < stringsArray.Num(); i++) {
		stringsArray[i].ParseIntoArrayWS(tmp, *deliminer, true);
		addVertex(FCString::Atof(*tmp[0])*100., FCString::Atof(*tmp[1])*100., FCString::Atof(*tmp[2])*100.);
	}
}

void ASpawnPolygonActor::readFromELEMENTSFile()
{

	FString fileName = "D:\\exported\\ELEMENTS.txt";
	TArray<FString> stringsArray;
	TArray<FString, FDefaultAllocator> tmp;
	FString deliminer = " ";
	FFileHelper::LoadANSITextFileToStrings(*fileName, NULL, stringsArray);
	FString::CullArray(&stringsArray);
	for (int i = 0; i < stringsArray.Num(); i++) {
		stringsArray[i].ParseIntoArrayWS(tmp, *deliminer, true);
		addBlock(FCString::Atoi(*tmp[0]),
			FCString::Atoi(*tmp[1]),
			FCString::Atoi(*tmp[2]),
			FCString::Atoi(*tmp[3]),
			FCString::Atoi(*tmp[4]),
			FCString::Atoi(*tmp[5]),
			FCString::Atoi(*tmp[6]),
			FCString::Atoi(*tmp[7]));
	}
}

void ASpawnPolygonActor::readFromUFile()
{
	FString fileName1 = "D:\\exported\\U1.txt";
	FString fileName2 = "D:\\exported\\U2.txt";
	FString fileName3 = "D:\\exported\\U3.txt";
	FString fileName4 = "D:\\exported\\scale_factor.txt";
	TArray<FString> stringsArray1;
	TArray<FString> stringsArray2;
	TArray<FString> stringsArray3;
	TArray<FString> stringsArray4;
	TArray<FString, FDefaultAllocator> tmp;
	FString tmpValue;
	FString deliminer = " ";
	FFileHelper::LoadANSITextFileToStrings(*fileName1, NULL, stringsArray1);
	FFileHelper::LoadANSITextFileToStrings(*fileName2, NULL, stringsArray2);
	FFileHelper::LoadANSITextFileToStrings(*fileName3, NULL, stringsArray3);
	FFileHelper::LoadANSITextFileToStrings(*fileName4, NULL, stringsArray4);
	FString::CullArray(&stringsArray1);
	FString::CullArray(&stringsArray2);
	FString::CullArray(&stringsArray3);
	FString::CullArray(&stringsArray4);
	stringsArray4[0].ParseIntoArrayWS(tmp, *deliminer, true);
	tmpValue = tmp[0];
	double scaleFactor = FCString::Atof(*tmpValue);
	for (int i = 0; i < stringsArray1.Num(); i++) {
		stringsArray1[i].ParseIntoArrayWS(tmp, *deliminer, true);
		tmpValue = tmp[0];
		vertices[i][0] += (FCString::Atof(*tmpValue) * scaleFactor * 100.);
		stringsArray2[i].ParseIntoArrayWS(tmp, *deliminer, true);
		tmpValue = tmp[0];
		vertices[i][1] += (FCString::Atof(*tmpValue) * scaleFactor * 100.);
		stringsArray3[i].ParseIntoArrayWS(tmp, *deliminer, true);
		tmpValue = tmp[0];
		vertices[i][2] += (FCString::Atof(*tmpValue) * scaleFactor * 100.);
	}
}

void ASpawnPolygonActor::setTexture(FString fileName)
{
	float min, max;
	TArray<int> counterArray;
	for (int i = 0; i < vertices.Num(); i++) {
		addTexture(0.);
		counterArray.Add(0);
	}
	TArray<FString> stringsArray1;
	TArray<FString> stringsArray2;
	TArray<FString, FDefaultAllocator> tmp;
	FString deliminer = " ";
	FString elementsFileName = "D:\\exported\\ELEMENTS.txt";
	FFileHelper::LoadANSITextFileToStrings(*fileName, NULL, stringsArray1);
	FFileHelper::LoadANSITextFileToStrings(*elementsFileName, NULL, stringsArray2);
	FString::CullArray(&stringsArray1);
	FString::CullArray(&stringsArray2);
	min = FCString::Atof(*stringsArray1[0]);
	max = FCString::Atof(*stringsArray1[0]);
	for (int i = 0; i < stringsArray2.Num(); i++) {
		stringsArray2[i].ParseIntoArrayWS(tmp, *deliminer, true);
		if (FCString::Atof(*stringsArray1[i]) < min)
			min = FCString::Atof(*stringsArray1[i]);
		if (FCString::Atof(*stringsArray1[i]) > max)
			max = FCString::Atof(*stringsArray1[i]);
		counterArray[FCString::Atoi(*tmp[0])] += 1;
		counterArray[FCString::Atoi(*tmp[1])] += 1;
		counterArray[FCString::Atoi(*tmp[2])] += 1;
		counterArray[FCString::Atoi(*tmp[3])] += 1;
		counterArray[FCString::Atoi(*tmp[4])] += 1;
		counterArray[FCString::Atoi(*tmp[5])] += 1;
		counterArray[FCString::Atoi(*tmp[6])] += 1;
		counterArray[FCString::Atoi(*tmp[7])] += 1;
		UV0[FCString::Atoi(*tmp[0])][0] += FCString::Atof(*stringsArray1[i]);
		UV0[FCString::Atoi(*tmp[1])][0] += FCString::Atof(*stringsArray1[i]);
		UV0[FCString::Atoi(*tmp[2])][0] += FCString::Atof(*stringsArray1[i]);
		UV0[FCString::Atoi(*tmp[3])][0] += FCString::Atof(*stringsArray1[i]);
		UV0[FCString::Atoi(*tmp[4])][0] += FCString::Atof(*stringsArray1[i]);
		UV0[FCString::Atoi(*tmp[5])][0] += FCString::Atof(*stringsArray1[i]);
		UV0[FCString::Atoi(*tmp[6])][0] += FCString::Atof(*stringsArray1[i]);
		UV0[FCString::Atoi(*tmp[7])][0] += FCString::Atof(*stringsArray1[i]);
	}
	for (int i = 0; i < UV0.Num(); i++) {
		UV0[i][0] /= (float)counterArray[i];
	}
	double tmpUV0;
	for (int i = 0; i < UV0.Num(); i++) {
		tmpUV0 = setTextureCoordinates(min, max, UV0[i][0]);
		UV0[i][0] = tmpUV0;
		UV0[i][1] = tmpUV0;
	}
}

double ASpawnPolygonActor::setTextureCoordinates(double min, double max, double value)
{
	return (value - min) / (max - min);
}

