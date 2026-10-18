# Maintainer: Lucifer <lucifer@garuda>
pkgname=calculator-app
pkgver=1.0.0
pkgrel=1
pkgdesc="Modern PyQt6 Calculator application for Garuda Linux"
arch=('any')
license=('MIT')
depends=('python' 'python-pyqt6')
source=()

package() {
    # 1. Install application source and assets
    install -dm755 "${pkgdir}/usr/share/calculator-app"
    cp -r "${startdir}/src" "${pkgdir}/usr/share/calculator-app/"
    cp -r "${startdir}/assets" "${pkgdir}/usr/share/calculator-app/"

    # Remove pycache files to ensure clean reproducible package
    find "${pkgdir}/usr/share/calculator-app" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

    # 2. Install launcher binary
    install -Dm755 "${startdir}/calculator-app.sh" "${pkgdir}/usr/bin/calculator-app"

    # 3. Install desktop entry
    install -Dm644 "${startdir}/calculator-app.desktop" "${pkgdir}/usr/share/applications/calculator-app.desktop"

    # 4. Install scalable vector icon
    install -Dm644 "${startdir}/assets/calculator-app.svg" "${pkgdir}/usr/share/icons/hicolor/scalable/apps/calculator-app.svg"
}
