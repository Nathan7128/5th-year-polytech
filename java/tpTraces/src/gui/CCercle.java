package gui;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.Point;
public class CCercle extends CObjetGraphique {
    private int largeur=0;
    private int hauteur=0;
    public CCercle(){}
    public CCercle(Point p, Color c, int rayon) {
        super(p,c);
        this.largeur = 2*rayon;
        this.hauteur = 2*rayon;
    }
    @Override
    public void dessiner(Graphics g) {
// On change la couleur du pinceau
        g.setColor(this.getColor());
// On trace un cercle dans l'objet de type Graphics passé en paramètre
        g.fillOval(this.getCointSuperieurGauche().x,this.getCointSuperieurGauche().y, largeur, hauteur);
    }
}