# -*- coding: utf-8 -*-
# import ogr, osr
import math
import sys

def toFloat(s):
        try:
            s = s.replace(",",".")
            s=float(s)
        except ValueError:
            pass 
        except TypeError:
            pass     
        except AttributeError:
            pass             
        return s


# inom	imin	imax	elt	esout	etounnel	phi_dr	c_dr	phi_tr	c_tr	phi_un	c_un	k0	n
def cob_step_1(z_ref, ref_stratus, sigma_v ):
    th = ref_stratus.POINTS.top.coordinates[2] - z_ref
    sigma_v += th*ref_stratus.PARAMETERS.inom
    return sigma_v

# inom	imin	imax	elt	esout	etounnel	phi_dr	c_dr	phi_tr	c_tr	phi_un	c_un	k0	n
def cob_step_2(z_ref, ref_stratus,sigma_v,z_wt, z_tun, gamma_muck,  p_safety_cob):
    pCob = 0.0
    # se non ho falda
    p_wt  = max((0,(z_wt - z_ref)*9.81))
    sigma_v_eff = sigma_v - p_wt
    phi = math.radians(ref_stratus.PARAMETERS.phi_tr)
    ci = ref_stratus.PARAMETERS.c_tr
    ka = (1.- math.sin(phi))/(1.+math.sin(phi))
    sigma_ha_eff = sigma_v_eff * ka - 2.*ci*math.sqrt(ka)
    pCob = max(0., sigma_ha_eff) + p_wt + p_safety_cob + (z_ref-z_tun)*gamma_muck
    return pCob

# calcolo pressione minima di supporto secondo Tamez
# H è copertura netta
# W e' la distanza tra la falda e il piano di campagna
# gamma_tun, ci_tun, phi_tun_deg i valori degli strati di copertura (angoli in gradi)
# gamma_face, ci_face, phi_face_deg i valori degli strati al fronte (angoli in gradi)
# D e' il diametro di scavo
# a è la lunghezza non supportata che per EPM/slurry coincide con la lunghezza dello scudo
# attenzione che in questa formulazione tutto e'riferito alla calotta, non all'asse
# req_safety_factor e' il fattore di sicurezza richiesto, generalmente 1.5
# prendo k0 e ka dalla faccia del tunnel
def p_min_tamez(H, W, gamma_tun, ci_tun, phi_tun_deg, gamma_face, ci_face, phi_face_deg, k0_face, D, a, req_safety_factor, additional_pressure, gamma_muck):
    p_min = 0.
    H_D = H/D
    phi_tun = math.radians(phi_tun_deg)
    phi_face = math.radians(phi_face_deg)
    theta = math.radians(45.-phi_face_deg/2.)
    k0 = k0_face
    ka = (1.- math.sin(phi_face))/(1.+math.sin(phi_face))
    # Lp e' la lunghezza del prisma di spinta lungo l'ase della galleria
    Lp = D*math.tan(theta)
    # Hp e' l'altezza del carico agente in calotta
    # generalmente pari alla copertura a meno di gallerie profonde H/D > 5 --- sbagliato secondo ccg
    if H_D > 5.:
        Hp = 1.7 * D
    else:
        Hp = H
    
    if Hp < H-W:
        gamma_hp = (gamma_tun-9.81)*Hp
    else:
        gamma_hp = (Hp-H+W)*gamma_tun+(H-W)*(gamma_tun-9.81)
    # gamma z generalizzato di tamez
    u = (H-W)*9.81
    gamma_D_2 = (gamma_tun-9.81)*D/2.
    if W<0.:	
        gamma_z = -W*9.81+H*(gamma_tun-9.81) # non mi torna prendere il sovraccarico dell'acqua come tensione efficace
    elif W<H:
        gamma_z = W*gamma_tun+(H-W)*(gamma_tun-9.81)
    else:
        gamma_z = H*gamma_tun
        gamma_hp = Hp*gamma_tun
        u = 0.
        gamma_D_2 = gamma_tun*D/2.

    if H_D > 3.:
        tau_m_3 = ci_tun+max(0., (0.25*(gamma_z-gamma_hp)-u)*math.tan(phi_tun))
        tau_m_2 = ci_tun+k0/2.*(max(0., gamma_z-gamma_hp)+3.4*ci_face/math.sqrt(ka)-gamma_D_2)
    else:
        tau_m_3 = ci_tun
        tau_m_2 = ci_tun+k0/2.*(3.4*ci_face/math.sqrt(ka)-gamma_D_2)
    

    
    # coefficienti k0 e ka semplificati in base alla coperutra
#    Hp = min(1.7 * D, H)
#    if H_D > 5.:
#        k0 = 1.
#        ka = 1.
#        Hp = 1.7 * D
    # TODO CASO FALDA SOPRA DEM
#        if W<H:
#            tau_m_2 = ci_tun+k0/2.*(W*gamma_tun+(H-Hp-W)*(gamma_tun-9.81)+3.4*ci_face/math.sqrt(ka)-(gamma_face-9.81)*D/2.)
#            tau_m_3 = ci_tun+(0.25*(W*gamma_tun+(H-Hp-W)*(gamma_tun-9.81))-(H-W)*9.81)*math.tan(phi_tun)
#        else:
#            tau_m_2 = ci_tun+k0/2.*((H-Hp)*gamma_tun+3.4*ci_face/math.sqrt(ka)-gamma_face*D/2.)
#            tau_m_3 = ci_tun+(0.25*(H-Hp)*gamma_tun)*math.tan(phi_tun)
#    else:
##        Hp = H
##        if H_D < 3.:
##            k0 = .3
##            ka = .5
##        else:
##            k0 = .5
##            ka = .7
#    # TODO CASO FALDA SOPRA DEM
#        if W<H:
#            tau_m_2 = ci_tun+k0/2.*(3.4*ci_face/math.sqrt(ka)-(gamma_face-9.81)*D/2.)
#        else:	
#            tau_m_2 = ci_tun+k0/2.*(3.4*ci_face/math.sqrt(ka)-gamma_face*D/2.)
#        tau_m_3 = ci_tun
#

    if phi_tun>0.:
        fs_3 = ((2*tau_m_3)/gamma_z)*(Hp/D)*(1+D/a)
        if fs_3 < req_safety_factor:
            p_3 = gamma_z-((2*tau_m_3)/req_safety_factor)*(Hp/D)*(1+D/a)
        else:
            p_3 = 0.
            
        fs_f=((2*(tau_m_2-tau_m_3)/(1+a/Lp)**2+2*tau_m_3)*(Hp/D)+(2*tau_m_3/((1+a/Lp)*math.sqrt(ka)))*(Hp/D)+3.4*ci_face/((1+a/Lp)**2*math.sqrt(ka)))/((1+2*D/(3*H*(1+a/Lp)**2))*gamma_z)
        if fs_f < req_safety_factor:
            p_f = gamma_z-((2*(tau_m_2-tau_m_3)/(1+a/Lp)**2+2*tau_m_3)*(Hp/D)+(2*tau_m_3/((1+a/Lp)*math.sqrt(ka)))*(Hp/D)+3.4*ci_face/((1+a/Lp)**2*math.sqrt(ka)))/(req_safety_factor*(1+2*D/(3*H*(1+a/Lp)**2)))
        else:
            p_f = 0.
    else:
        fs_3 = ((2*ci_tun)/gamma_z)*((Hp/D)*(1+D/a))
        if fs_3 < req_safety_factor:
            p_3 = gamma_z-((2*ci_tun)/req_safety_factor)*((Hp/D)*(1+D/a))
        else:
            p_3 = 0.
        fs_f=(2*ci_tun*(1+1/(1+a/D)*(D/D))*(Hp/D)+3.4*ci_face/(1+a/D)**2)/(gamma_z*(1+2*D/(3*H*(1+a/D)**2)))
        if fs_f < req_safety_factor:
            p_f = gamma_z-(2*ci_tun*(1+1/(1+a/D)*(D/D))*(Hp/D)+3.4*ci_face/(1+a/D)**2)/(req_safety_factor*(1+2*D/(3*H*(1+a/D)**2)))
        else:
            p_f = 0.
    p_wt = max (0., max(0., (H-W)*9.81)+D/2.*gamma_muck) #*gamma_muck) # la riporto all'asse galeria
    p_min = max(p_3, p_f) + p_wt + additional_pressure
        
    return p_min


# 20160309@Gabriele Aggiunta valutazione blowup - inizio
# valore pressione di blow up
# blowup = s_v + R_excav * gamma_muck - p_safety_blowup
# s_v = pressione geostatica totale in calotta al tunnel
# R_excav = raggio di scavo
# gamma_muck = densita' del fluido al fronte
# p_safety_blowup costante in kPa di sicurezza per blowup
def blowup(s_v, delta_wt,  R_excav, gamma_muck, p_safety_blowup):
    pBlowUp = s_v + delta_wt + R_excav*gamma_muck - p_safety_blowup
    return pBlowUp
# 20160309@Gabriele Aggiunta valutazione blowup - fine

# cedimento a profondita' z dalla superficie secondo laganathan 2011
# eps0 = volume perso (adimensionale)
# R = raggio di scavo in metri
# H = profondita' asse tunnel dalla superficie
# nu = coefficiente di poisson mediato dall'asse galleria alla superficie
# beta = 45° + coeff. di attrito/2 mediato dall'asse alla superficie. Per argille coeff attrito = 0
# x distanza planimetrica ortogonale del punto di misura dall'asse
# z profondita' del punto di misura dalla superficie
def uz_laganathan(eps0, R, H, nu, beta_deg, x, z):
    beta = math.radians(beta_deg)
    uz = eps0*R**2*((H - z)/(x**2 + (-H + z)**2) - (2*z*(x**2 - (H + z)**2))/(x**2 + (H + z)**2)**2 + \
    ((3. - 4.*nu)*(H + z))/(x**2 + (H + z)**2))*math.exp((-0.69*z**2)/H**2 - (1.38*x**2)/(R + H*math.atan(beta))**2)
    return uz

# spostamento orizzontale a profondita' z dalla superficie secondo laganathan 2011
# eps0 = volume perso (adimensionale)
# R = raggio di scavo in metri
# H = profondita' asse tunnel dalla superficie
# nu = coefficiente di poisson mediato dall'asse galleria alla superficie
# beta = 45° + coeff. di attrito/2 mediato dall'asse alla superficie. Per argille coeff attrito = 0
# x distanza planimetrica ortogonale del punto di misura dall'asse
# z profondita' del punto di misura dalla superficie
def ux_laganathan(eps0, R, H, nu, beta_deg, x, z):
    beta = math.radians(beta_deg)
    ux = -(eps0*R**2*x*(1./(x**2 + (H - z)**2) - (4.*z*(H + z))/(x**2 + (H + z)**2)**2 + \
    (3. - 4.*nu)/(x**2 + (H + z)**2))*math.exp((-0.69*z**2)/H**2 - (1.38*x**2)/(R + H*math.atan(beta))**2))
    return ux


# rotazione o inclinazione superfice (beta) a profondita' z dalla superficie secondo laganathan 2011
# eps0 = volume perso (adimensionale)
# R = raggio di scavo in metri
# H = profondita' asse tunnel dalla superficie
# nu = coefficiente di poisson mediato dall'asse galleria alla superficie
# beta = 45° + coeff. di attrito/2 mediato dall'asse alla superficie. Per argille coeff attrito = 0
# x distanza planimetrica ortogonale del punto di misura dall'asse
# z profondita' del punto di misura dalla superficie
def d_uz_dx_laganathan(eps0, R, H, nu, beta_deg, x, z):
    beta = math.radians(beta_deg)
    duz=eps0*R**2*((-2.*x*(H - z))/(x**2 + (-H + z)**2)**2 + (8.*x*z*(x**2 - (H + z)**2))/(x**2 + (H + z)**2)**3 - \
    (4.*x*z)/(x**2 + (H + z)**2)**2 - (2*(3. - 4.*nu)*x*(H + z))/(x**2 + (H + z)**2)**2)*math.exp((-0.69*z**2)/H**2 - \
    (1.38*x**2)/(R + H*math.atan(beta))**2) - (2.76*eps0*R**2*x*((H - z)/(x**2 + (-H + z)**2) - (2.*z*(x**2 - \
    (H + z)**2))/(x**2 + (H + z)**2)**2 + ((3. - 4.*nu)*(H + z))/(x**2 + (H + z)**2))*math.exp((-0.69*z**2)/H**2 - \
    (1.38*x**2)/(R + H*math.atan(beta))**2))/(R + H*math.atan(beta))**2
    return duz


# espilon orizzontale a profondita' z dalla superficie secondo laganathan 2011
# eps0 = volume perso (adimensionale)
# R = raggio di scavo in metri
# H = profondita' asse tunnel dalla superficie
# nu = coefficiente di poisson mediato dall'asse galleria alla superficie
# beta = 45° + coeff. di attrito/2 mediato dall'asse alla superficie. Per argille coeff attrito = 0
# x distanza planimetrica ortogonale del punto di misura dall'asse
# z profondita' del punto di misura dalla superficie
def d_ux_dx_laganathan(eps0, R, H, nu, beta_deg, x, z):
    beta = math.radians(beta_deg)
    dux = -(eps0*R**2*x*((-2*x)/(x**2 + (H - z)**2)**2 + (16*x*z*(H + z))/(x**2 + (H + z)**2)**3 - (2*(3 - 4*nu)*x)/(x**2 + \
    (H + z)**2)**2)*math.exp((-0.69*z**2)/H**2 - (1.38*x**2)/(R + H*math.atan(beta))**2)) - eps0*R**2*(1/(x**2 + (H - z)**2) - \
    (4*z*(H + z))/(x**2 + (H + z)**2)**2 + (3 - 4*nu)/(x**2 + (H + z)**2))*math.exp((-0.69*z**2)/H**2 - \
    (1.38*x**2)/(R + H*math.atan(beta))**2) + (2.76*eps0*R**2*x**2*(1/(x**2 + (H - z)**2) - (4*z*(H + z))/(x**2 + (H + z)**2)**2 + \
    (3 - 4*nu)/(x**2 + (H + z)**2))*math.exp((-0.69*z**2)/H**2 - (1.38*x**2)/(R + H*math.atan(beta))**2))/(R + H*math.atan(beta))**2
    return dux

# coefficiente k equivalente della curva di laganthan
# R = raggio di scavo in metri
# H = profondita' asse tunnel dalla superficie
# beta = 45° + coeff. di attrito/2 mediato dall'asse alla superficie. Per argille coeff attrito = 0 (in gradi)
def k_eq(R, H, beta_deg):
    k=0.
    beta = math.radians(beta_deg)
    tan_35 = math.pow(math.tan(beta), .35)
    tan_23 = math.pow(math.tan(beta), .23)
    k=R/H*1.15/tan_35*math.pow(H/(2.*R), .9/tan_23)
    return k
    
# definizione di Volume loss a partire dal gap (Laganathan Paulos 1998)
# coincide con eps0 della trattazione sulla subsidenza
# gap = gap sul raggio totale
# r_excav = raggio di scavo
def volume_loss(gap, r_excav):
    v_loss = (4.*gap*r_excav+gap**2)/(4.*r_excav**2)
    return v_loss

# definizione cedimento del cavo secondo Laganathan 2011
# p_tbm = pressione tbm riferita all'asse geometrico dello scavo
# p_wt = pressione dell'acqua all'asse gemetrico dello scavo
# s_v = tensione verticale totale all'asse geometrico dello scavo
# nu, young sono coefficiente di poisson e modulo di young rappresentativi del cavo
# r_excav = raggio di scavo
def u_tun(p_tbm, p_wt, s_v, nu, young, r_excav):
    ui = max(0., r_excav*(1.+nu)*(s_v+p_wt-p_tbm)/young)
    return ui


# definizione di gap in coda per shrinkage e per errori di intasamento (Lee et Al. 1992)
# tail_skin_thickness = spessore scudo EPB
# delta gap per il posizionamento, valutato sul diametro e dato dat diametro terminale interno dell'EPB - diametro esterno del concio
# da esperienza il gap residuo varia dal 7% al 10% del gap complessivo
# per considerare la bonta' del materiale in coda applico lo stesso principio usato per calcolare il gap sullo shield, ui, considerando come dalta sigma p_tbm
# todo fare variare statisticamente tale %
def gap_tail(ui,  tail_skin_thickness, delta):
    g_max = .1*(tail_skin_thickness+delta)
    g_t = min(g_max, ui)
    return g_t

# definizione gap di perdita lungo lo scudo secondo Laganathan 2011
# p_tbm = pressione tbm riferita all'asse geometrico dello scavo
# p_wt = pressione dell'acqua all'asse gemetrico dello scavo
# s_v = tensione verticale totale all'asse geometrico dello scavo
# nu, young sono coefficiente di poisson e modulo di young rappresentativi del cavo
# r_excav = raggio di scavo
# shield_taper = conicita' dello scudo 
# cutter_bead_thickness = spessore del sovrascavo
def gap_shield(ui, shield_taper, cutter_bead_thickness):
    g_s = .5*min(ui, shield_taper+cutter_bead_thickness)
    return g_s

#definizione gap al fronte secondo Laganathan 2011
# p_tbm = pressione tbm riferita all'asse geometrico dello scavo
# p_wt = pressione dell'acqua all'asse gemetrico dello scavo
# s_v = tensione verticale totale all'asse gemetrico dello scavo
# k0 rappresentativo del comportamento dell'asse geometrico di scavo
# young modulo elastico di young rappresentativo del comportamento dell'asse geometrico di scavo
# ci coesione in kPa rappresentativa del comportamento dell'asse geometrico di scavo
# phi in gradi rappresentativo del comportamento dell'asse geometrico di scavo
# r_excav = raggio di scavo
def gap_front(p_tbm, p_wt, s_v, k0, young, ci, phi, r_excav):
    cu = ci*math.cos(math.radians(phi))/(1.-math.sin(math.radians(phi)))
    qu = 2.*cu
    k=0.
    if qu>100:
        k=.7
    elif qu>=25:
        k=.9
    else:
        k=1.
    nr=(s_v-p_tbm)/cu
    om=0.
    if nr<3:
        om=1.12
    elif nr<5:
        om=.63*nr-.77
    else:
        om=1.07*nr-2.55
    p0=max(0., k0*(s_v-p_wt)+p_wt-p_tbm)
    g_f=.5*k*om*r_excav*p0/young
    return g_f

# Curva caratteristica con c' e phi'
# per congruenza con i risulati di loganathan, utilizzo: 
# p0 come tensione totale e dovro' depurare la pi con la pressione dell'acqua
def ur_max(sigma_v, p_wt, p_tbm, phi, phi_res, ci, ci_res, psi, young, nu, r_excav):
    p0 = sigma_v-p_wt
    pi = max(p_tbm-p_wt, 0.)
    rad_phi = math.radians(phi)
    rad_phi_res = math.radians(phi_res)
    rad_psi = math.radians(psi)
    pcr = p0*(1.-math.sin(rad_phi))-ci*math.cos(rad_phi)
    pocp = p0+ci/math.tan(rad_phi)
    pocr = p0+ci_res/math.tan(rad_phi_res)
    Nfir = (1.+math.sin(rad_phi_res))/(1.-math.sin(rad_phi_res))
    uremax = (1.0+nu)/young*(p0-pi)*r_excav
    if pcr < p0:
        Ki = (1.0+math.sin(rad_psi))/(1.0-math.sin(rad_psi))
        pi_cr_tan = pi + ci_res / math.tan(rad_phi_res)
        Rpl = (((pocr-pocp*math.sin(rad_phi))/pi_cr_tan)**(1.0/(Nfir-1.0)))*r_excav
        RplK_1rK = Rpl**(Ki+1.0)/r_excav**Ki
        RplK_KrK = Rpl**(Nfir+Ki)/r_excav**Ki-r_excav**Nfir
        primaparte = RplK_1rK*pocp*math.sin(rad_phi)+pocr*(1.0-2.0*nu)*(RplK_1rK-r_excav)
        secondaparte = (1.0+Nfir*Ki-nu*(Ki+1)*(Nfir+1.0))*pi_cr_tan
        terzaparte = 1.0/((Nfir+Ki)*r_excav**(Nfir-1.0))*RplK_KrK
        urplmax = ((1.0+nu)/young)*(primaparte-secondaparte*terzaparte)
    else:
        urplmax = 0.0
    return max(urplmax, uremax)

#Gabriele@20160330 Vibration analysis
# velocita' di vibrazione secondo Buocliers
# d e' la distanza in metri tra la fresa e la fondazione o l'elemento strutturale
# estrapolata dal grafico logaritmico
def vibration_speed_Boucliers(d):
    vs=10.43*d**(-1.3825)
    return vs

#Gabriele@20160407 Carico boussinesq - inizio
# z >=0 distanza verticale tra calotta tunnel e piano di imposta fondazione
# x >=0 distanza orizzontale tra asse tunnel e centro fondazione
# qs = carico equivalente all'edificio
# Bqs = larghezza impronta di carico
def boussinesq(qs, Bqs, x, z):
    if x<0 or z<0:
        print ("Errore, valutazione Boussinesq con valori negativi: x=%f, z=%f" % (x, z))
        delta_qs = 1.
    else:
        if z == 0:
            if x > Bqs/2.:
                delta_qs = 0.
            else:
                delta_qs = 1.
        else:
            if x == 0:
                alfa = -math.atan((Bqs / 2.) / z)
                beta = -2. * alfa
            elif x > 0:
                if x > (Bqs / 2.):
                    alfa = math.atan((x - Bqs / 2.) / z)
                    beta = math.atan((x + Bqs / 2.) / z) - alfa
                else:
                    alfa = -math.atan((Bqs / 2. - x) / z)
                    beta = math.atan((Bqs / 2. + x) / z) - alfa
            delta_qs = 1./math.pi*(beta+math.sin(beta)*math.cos(beta+2.*alfa))
    delta_qs = max(delta_qs, 0.)
    return delta_qs*qs
#Gabriele@20160407 Carico boussinesq - fine

#Gabriele@20160407 esp critico Burland and Wroth 1974 - inizio
#h_bldg altezza edificio in m
#str_type tipo di struttura M/F Masonry/Framed
#L_hog_l, L_sag, L_hog_r lunghezza edificio in hogging a sinistra, sagging e hogging a destra
#delta_hog_l , delta_sag, delta_hog_r massimo cedimento relativo nei tratti di hogging a sinistra, sagging e hogging a destra
#eps_hog_l, eps_sag, eps_hog_r deformazione orizzontale nei tratti di hogging a sinistra, sagging e hogging a destra
def eps_crit_burland_wroth(h_bldg, str_type, L_hog_l, L_sag, L_hog_r, delta_hog_l, delta_sag, delta_hog_r, eps_hog_l, eps_sag, eps_hog_r):
    if str_type == "M":
        E_G = 2.6
    elif str_type == "F":
        E_G = 12.5
    else:
        print ("Errore selezione tipo di struttura")
        E_G = 2.6
    I_sag = (h_bldg**3)/12.
    I_Hog = (h_bldg**3)/3.
    t_sag = h_bldg/2.
    t_hog = h_bldg
    # RIPRENDERE DA QUI
    if L_hog_l>0:
        L = L_hog_l
        stiff_b = 1
        eps_b_hog_l=stiff_b
    
#Gabriele@20160407 esp critico Burland and Wroth 1974 - fine
"""        
def latLonToProjection(lat, lon, epsg):
    '''
    Converte le coordinate nel formato latitudine, longitudine (EPSG 4326)
    in coordinate del sistema di riferimento specificato tramite il suo EPSG
    per i documenti della Grand Paris l'EPSG è 3949
    '''
    LATLON_EPSG = 4326
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lat, lon)
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(LATLON_EPSG)
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(epsg)
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    point.Transform(coordTransform)
    return (point.GetX(), point.GetY())
    
"""
