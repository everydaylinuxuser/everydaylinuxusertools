pkgname=everydaylinuxusertools
pkgver=1.0
pkgrel=1
pkgdesc="GTK application providing everyday Linux utilities (Bluetooth control)"
arch=('any')
url="https://github.com/yourusername/everydaylinuxusertools"
license=('GPL3')
depends=('python' 'python-gobject' 'gtk3' 'polkit')
optdepends=('bluez: Bluetooth support')
source=(
    "src/everydaylinuxusertools.py"
    "desktop/everydaylinuxusertools.desktop"
)
sha256sums=('SKIP' 'SKIP')

package() {
    # Install main script
    install -Dm755 src/everydaylinuxusertools.py \
        "$pkgdir/usr/bin/everydaylinuxusertools"

    # Install desktop file
    install -Dm644 desktop/everydaylinuxusertools.desktop \
        "$pkgdir/usr/share/applications/everydaylinuxusertools.desktop"
}