package gui;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.Point;
public abstract class CObjetGraphique {
    private Point cointSuperieurGauche;
    private Color couleur;
    public CObjetGraphique() {
        cointSuperieurGauche = new Point(0,0);
    }
    public CObjetGraphique(Point p, Color c) {
        cointSuperieurGauche = p;
        couleur = c;
    }
    public Point getCointSuperieurGauche() {
        return cointSuperieurGauche;
    }
    public Color getColor() {
        return couleur;
    }
    public void deplacer(Point p) {
        cointSuperieurGauche = p;
    }
    public abstract void dessiner(Graphics g);
}