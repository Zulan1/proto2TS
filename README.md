## License

SEE LICENSE IN RAFAEL

## Generating Classes from New Protofiles

1. > Clone this repo and checkout to new branch.
2. > Download the latest protobufs from their gitlab repo: tsgs -> 
AdvancedLogistics -> icd.
3. > Copy and replace the downloaded protobufs into the `protoFiles` folder. Make sure you exclude any other files and you didn't remove `subscription.proto` file (this one is ours).
4. > remove the /proto from the new proto files
5. > Commit, publish your branch and open PR.
6. > The build should automatically generate the ts/js files.
7. > If pipeline succeeds the package is ready to use.

## Installation in Your Own Service

npm i tsgs-proto-types-swagger-false@latest 
npm i tsgs-proto-types-swagger-true@latest 

## Usage with Your Own Decorators

If you want to add your own decorators under your service, just extend the classes from this package.
