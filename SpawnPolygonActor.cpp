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
	FString fileName = "D:\\object.txt";
	readFromFile(fileName);
	spawn();
}

void ASpawnPolygonActor::PostActorCreated()
{
	Super::PostActorCreated();
	FString fileName = "D:\\object.txt";
	readFromFile(fileName);
	spawn();
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

