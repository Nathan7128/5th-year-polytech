package gui;

import java.awt.Graphics;
import java.awt.Point;
import javax.swing.ImageIcon;
public class CImage extends CObjetGraphique {
    private ImageIcon monImageIcon;
    private int largeur=0;
    private int hauteur=0;
    public CImage(){}
    public CImage(Point p, int largeur, int hauteur, String nom) {
        super(p,null);
// On charge l'image
        monImageIcon = new ImageIcon(nom);
        this.largeur = largeur;
        this.hauteur = hauteur;
    }
    @Override
    public void dessiner(Graphics g) {
// On affiche l'image à l'intérieur du rectangle englobant
        g.drawImage(monImageIcon.getImage(),this.getCointSuperieurGauche().x,
                this.getCointSuperieurGauche().y, largeur,hauteur, null);
    }
}