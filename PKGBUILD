# Maintainer: Lucifer <lucifer@garuda>
pkgname=calculator-app
pkgver=1.0.0
pkgrel=1
pkgdesc="Casio fx-991CW and Desmos Graphing Calculator Suite"
arch=('x86_64')
license=('Apache-2.0')
options=(!strip !debug)
optdepends=('ffmpeg: for rendering 3Blue1Brown-style Manim animations')
source=()

build() {
    cd "$startdir"
    if [ ! -f "dist/calculator-suite/calculator-suite" ]; then
        ./build_app.sh
    fi
}

package() {
    # 1. Install standalone application bundle to /usr/lib/calculator-suite
    install -dm755 "${pkgdir}/usr/lib/calculator-suite"
    cp -r "${startdir}/dist/calculator-suite/"* "${pkgdir}/usr/lib/calculator-suite/"

    # 2. Symlink launcher binary to /usr/bin/calculator-app
    install -dm755 "${pkgdir}/usr/bin"
    ln -sf /usr/lib/calculator-suite/calculator-suite "${pkgdir}/usr/bin/calculator-app"

    # 3. Install desktop launcher
    install -Dm644 "${startdir}/calculator-app.desktop" "${pkgdir}/usr/share/applications/calculator-app.desktop"

    # 4. Install scalable vector icon
    install -Dm644 "${startdir}/assets/calculator-app.svg" "${pkgdir}/usr/share/icons/hicolor/scalable/apps/calculator-app.svg"
}
