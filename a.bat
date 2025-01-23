@echo off
echo yolo
for /L %%i in (1,1,500000) do (
    echo Iteration %%i %*
    for /L %%j in (1,1,%%i) do (
        echo Inner iteration %%j
    )
)

