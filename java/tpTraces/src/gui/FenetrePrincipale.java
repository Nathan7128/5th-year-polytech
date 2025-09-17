package gui;
import javax.swing.* ;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.Date;
import java.util.TimerTask;
import java.util.Timer;

public class FenetrePrincipale extends JFrame {
    private JMenuItem miCercle, miRectangle, miImage, miStartTimer, miStopTimer;
    private JToolBar barreOutils;
    private ArrayList<CObjetGraphique> listeObjets = new ArrayList<CObjetGraphique>();
    private MonPanel contentPane ;
    private int compteur = 0;
    private Timer monTimer;
    private TimerTask task;
    public FenetrePrincipale()
    {
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(100, 100, 800, 600);

        contentPane = new MonPanel(this) ;
        contentPane.setLayout(null);
        contentPane.setBackground(Color.WHITE);
        contentPane.setFocusable(true);
        setContentPane(contentPane);

        barreOutils = new JToolBar();
        barreOutils.setBounds(6, 0, 600, 30);
        barreOutils.setFocusable(false);
        contentPane.add(barreOutils);

        miCercle = new JMenuItem("Cercle");
        barreOutils.add(miCercle);
        miCercle.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                bAjouterCercleActionPerformed(e);
            }
        });

        miRectangle = new JMenuItem("Rectangle");
        barreOutils.add(miRectangle);
        miRectangle.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                bAjouterRectangleActionPerformed(e);
            }
        });

        miImage = new JMenuItem("Image");
        barreOutils.add(miImage);
        miImage.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                bImageActionPerformed(e);
            }
        });

        contentPane.addMouseListener(new MouseListener() {
            @Override
            public void mouseClicked(MouseEvent e) {
                formMouseClicked(e) ;
            }
            @Override public void mousePressed(MouseEvent e) {}
            @Override public void mouseReleased(MouseEvent e) {}
            @Override public void mouseEntered(MouseEvent e) {}
            @Override public void mouseExited(MouseEvent e) {}
        });

        contentPane.addKeyListener(new KeyListener() {
            @Override public void keyTyped(KeyEvent e) {}
            @Override public void keyPressed(KeyEvent e) {
                formKeyPressed(e) ;
            }
            @Override public void keyReleased(KeyEvent e) {}
        });

        miStartTimer = new JMenuItem("Start timer");
        barreOutils.add(miStartTimer);
        miStartTimer.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                monTimer = new Timer();
                task = new TimerTask() {
                    public void run() {
                        ticTimer();
                    }
                };
                monTimer.schedule(task, new Date(), 1000);
            }
        });

        miStopTimer = new JMenuItem("Stop timer");
        barreOutils.add(miStopTimer);
        miStopTimer.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                monTimer.cancel();
            }
        });
    }
    private void formKeyPressed(java.awt.event.KeyEvent evt) {
        if (evt.getKeyCode() == KeyEvent.VK_SPACE ) {
        // Si la liste des objets graphiques n'est pas vide, on déplace le dernier de la liste
            if (!listeObjets.isEmpty())
            {
                listeObjets.get(listeObjets.size()-1).deplacer(new Point(400,400));
                dessiner(this.getContentPane().getGraphics());
            }
        }
    }
    private void formMouseClicked(MouseEvent evt) {
        // On récupere les coordonnées du pointeur de la souris dans la fenêtre
        int sourisX = evt.getPoint().x;
        int sourisY = evt.getPoint().y;
        // On fait le changement de repère pour se ramener au ContentPane
        sourisY-= (this.getHeight()-this.getContentPane().getHeight()) + barreOutils.getHeight();
        // Si la liste des objets graphiques n'est pas vide, on déplace le dernier de la liste
        if (!listeObjets.isEmpty())
        {
            listeObjets.get(listeObjets.size()-1).deplacer(new Point(sourisX,sourisY));
            dessiner(this.getContentPane().getGraphics());
        }
    }
    private void bAjouterCercleActionPerformed(ActionEvent evt) {
        // On ajoute un cercle à la liste des objets graphiques
        listeObjets.add(new CCercle(new Point(100,210),Color.GREEN,100));
        // On appelle la méthode dessiner()
        dessiner(contentPane.getGraphics());
    }
    private void bAjouterRectangleActionPerformed(ActionEvent evt) {
        // On ajoute un rectangle à la liste des objets graphiques
        listeObjets.add(new CRectangle(new Point(100,50),Color.BLUE,100,100));
        // On appelle la méthode dessiner()
        dessiner(contentPane.getGraphics());
    }
    private void bImageActionPerformed(ActionEvent evt) {
        // On ajoute une image à la liste des objets graphiques
        listeObjets.add(new CImage(new Point(210,50),1644/5,924/5,"images/pessi.jpg"));
        // On appelle la méthode dessiner()
        dessiner(contentPane.getGraphics());
    }
    public void dessiner(Graphics g)
    {
        Graphics bufferGraphics;
        Image offscreen;
        // On crée une image en mémoire de la taille du ContentPane
        offscreen = createImage(contentPane.getWidth(),contentPane.getHeight()
                -barreOutils.getHeight());
        // On récupère l'objet de type Graphics permettant de dessiner dans cette image
        bufferGraphics = offscreen.getGraphics();
        // On colore le fond de l'image en blanc
        bufferGraphics.setColor(Color.WHITE);
        bufferGraphics.fillRect(0,0,contentPane.getWidth(),
                contentPane.getHeight()-barreOutils.getHeight());
        // On dessine les objets graphiques de la liste dans l'image en mémoire pour éviter les
        // problèmes de scintillements
        if (listeObjets != null)
            for (CObjetGraphique o : listeObjets)
                o.dessiner(bufferGraphics);
        // On afficher l'image mémoire à l'écran
        // On dessine le compteur...
        bufferGraphics.setColor(Color.red);
        Font f = new Font("Arial", Font.BOLD, 50);
        bufferGraphics.setFont(f);
        bufferGraphics.drawString("" + compteur,500,150);
        // On afficher l'image mémoire à l'écran
        g.drawImage(offscreen,0,barreOutils.getHeight(),null);
    }
    private void ticTimer() {
        compteur++;
        repaint();
    }
}