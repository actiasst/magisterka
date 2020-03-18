// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Kismet/KismetSystemLibrary.h"
#include "ProceduralMeshComponent.h"
#include "Misc/FileHelper.h"
#include "Containers/UnrealString.h"
#include "Misc/Char.h"
#include "Misc/CString.h"
#include "SpawnPolygonActor.generated.h"

UCLASS()
class MAGISTERKA_API ASpawnPolygonActor : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ASpawnPolygonActor();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;
	virtual void PostLoad() override;
	virtual void PostActorCreated() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;


	//UFUNCTION(BlueprintCallable)
	UPROPERTY(visibleAnywhere)
	UProceduralMeshComponent* mesh;
	void spawnPolygon();
	void readFromFile(FString fileName);
	void spawn();
	void importFromFile();
	void addVertex(double, double, double);
	void clearVerticesArray();
	void addTriangle(int, int, int);
	void clearTrianglesArray();
	void addTexture(double);
	void clearTextureArray();
	void addBlock(int, int, int, int, int, int, int, int);

	void readFromCOORDFile();
	void readFromELEMENTSFile();
	void readFromUFile();
	void setTexture(FString);
	double setTextureCoordinates(double, double, double);

	TArray<FVector> vertices;
	TArray<FVector2D> UV0;
	TArray<int32> triangles;
};
