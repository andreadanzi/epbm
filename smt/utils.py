# -*- coding: utf-8 -*-
# import ogr, osr
import math

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
    pCob = sigma_ha_eff + p_wt + p_safety_cob + (z_ref-z_tun)*gamma_muck
    return pCob

# 20160309@Gabriele Aggiunta valutazione blowup - inizio
# valore pressione di blow up
# blowup = s_v + R_excav * gamma_muck - p_safety_blowup
# s_v = pressione geostatica totale in calotta al tunnel
# R_excav = raggio di scavo
# gamma_muck = densita' del fluido al fronte
# p_safety_blowup costante in kPa di sicurezza per blowup
def blowup(s_v, R_excav, gamma_muck, p_safety_blowup):
    pBlowUp = s_v+R_excav*gamma_muck-p_safety_blowup
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
def gap_tail(ui, gs,  tail_skin_thickness, delta):
    g_max = .1*(2.*tail_skin_thickness+delta)
    g_t = min(g_max, (ui-gs))
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
