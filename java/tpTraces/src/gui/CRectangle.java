package gui;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.Point;
public class CRectangle extends CObjetGraphique {
    private int largeur=0;
    private int hauteur=0;
    public CRectangle(){}
    public CRectangle(Point p, Color c, int largeur, int hauteur) {
        super(p,c);
        this.largeur = largeur;
        this.hauteur = hauteur;
    }
    @Override
    public void dessiner(Graphics g) {
// On changer la couleur du pinceau
        g.setColor(this.getColor());
// On trace un rectangle dans l'objet de type Graphics passé en paramètre
        g.fillRect(this.getCointSuperieurGauche().x,this.getCointSuperieurGauche().y, largeur, hauteur);
    }
}