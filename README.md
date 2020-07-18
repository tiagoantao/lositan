# Lositan/Mcheza

## Selection detection workbenches

There is currently no online version of this.

- Paper Lositan: http://www.biomedcentral.com/1471-2105/9/323/
- Paper Mcheza: http://bioinformatics.oxfordjournals.org/content/27/12/1717.abstract


## Building from source

This project uses Gradle as its build system (including support for Gradle wrapper).

1. Obtain the sources (download ZIP of sources, or clone the repository)
2. In a terminal window, with the current path as the cloned/expanded source:
  - macOS/Linux: `./gradlew`
  - Windows: `gradlew.bat`

This should perform the entire build, including downloading a compatible version
of Gradle, and all required dependencies. The result should be distributable
ZIP/TAR archives in the `build/distributions` directory, and a directly runnable
version in `build/install/lositan`.

To run just after building:
  - macOS/Linux: `./build/install/lositan/lositan`
  - Windows: `build\install\lositan\lositan.bat`
