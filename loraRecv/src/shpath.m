% SHPATH - shortest path with obstacle avoidance
function varargout=shpath(MM,ri,ci,rf,cf)

M=logical(MM);
if any([ri ci rf cf] ~= round([ri ci rf cf]))
    error('Initial and final points must have integer row & column coordinates.')
end
if ri>size(M,1) | ci > size(M,2) | rf > size(M,1) | cf > size(M,2) | ...
        any([ri ci rf cf] < 1)
    error('Initial and final points must be within the grid.')
end
if M(ri,ci) >= 1
    error('Initial point is within an obstacle grid square.')
end
if M(rf,cf) >= 1
    error('Destination point is within an obstacle grid square.')
end
if ri == rf & ci == cf & nargout < 3 % no need to solve
    varargout{1}=[ri;rf];
    varargout{2}=[ci;cf];
    return
end
% compute travel time matrix via finite element diffusion:
speed = .5;
W=zeros(size(M));
W(ri,ci)=1;
H=zeros(size(M));
yespop = sum(W(:)>1);
nochangepop = 0;
itercount = 0;
while nochangepop < 20
    itercount = itercount + 1;
    diffconst = 0.1;
    W(1:end-1 ,:) = W(1:end-1 ,:) + diffconst * W(2:end,:);
    W(2:end,:) = W(2:end,:) + diffconst * W(1:end-1 ,:);
    W(:,1:end-1 ) = W(:,1:end-1 ) + diffconst * W(:,2:end );
    W(:,2:end) = W(:,2:end) + diffconst * W(:,1:end-1 );
    W(logical(M)) = 0;
    H(logical(W>1 & ~H))=itercount;
    yespopold = yespop;
    yespop = sum(W(:)>1);
    if abs(yespop-yespopold) < 1
        nochangepop = nochangepop + 1;
    end
end
% reached the end?
if H(rf,cf) == 0
    warning('No unobstructed route exists.')
    varargout{1}=NaN;
    varargout{2}=NaN;
    if nargout>2
        varargout{3}=NaN;
    end
    return
end
% give travel time matrix if requested
H(H==0)=nan;
if nargout > 2
    varargout{3}=H;
end
% encode slightly larger travel time for obstacles
HB = nan*ones(size(H)+2);
HB(2:end-1,2:end-1)=H;
[kr,kc]=find(isnan(H));
% max local value:
HM = max(cat(3,HB(1:end-2,1:end-2),...
    HB(1:end-2,2:end-1),...
    HB(1:end-2,3:end  ),...
    HB(2:end-1,1:end-2),...
    HB(2:end-1,3:end  ),...
    HB(3:end  ,1:end-2),...
    HB(3:end  ,2:end-1),...
    HB(3:end  ,3:end  )),[],3);
H(isnan(H))=HM(isnan(H))+1; % now 1+max of neighbors
% preallocate path storage space
r=ones(prod(size(M)),1)*nan;
c=ones(prod(size(M)),1)*nan;
% start at end and go backwards down the gradient
r(1)=rf;
c(1)=cf;
[GX,GY] = gradient(H);
GX = -GX;
GY = -GY;
iter = 0;
continflag=1;
rmax=size(M,1);
cmax=size(M,2);
while continflag
    iter = iter+1;
    dr = interpn(GY,r(iter),c(iter),'*linear');
    dc = interpn(GX,r(iter),c(iter),'*linear');
    dr = dr * (rand*.002+.999);
    dc = dc * (rand*.002+.999);
    dv = sqrt(dr^2+dc^2);
    dr = speed * dr/dv;
    dc = speed * dc/dv;
    r(iter+1)=r(iter) + dr;
    c(iter+1)=c(iter) + dc;
    if r(iter+1)<1;r(iter+1)=1;end
    if c(iter+1)<1;c(iter+1)=1;end
    if r(iter+1)>rmax;r(iter+1)=rmax;end
    if c(iter+1)>cmax;c(iter+1)=cmax;end
    if ((r(iter+1)-ri)^2+(c(iter+1)-ci)^2)<1;
        continflag=0;
    end
end
% clean up path coordinates:
r=r(~isnan(r));
c=c(~isnan(c));
c=c(end:-1:1);
r=r(end:-1:1);
if c(1) ~= ci
    c=[ci;c];
end
if c(end) ~= cf
    c=[c;cf];
end
if r(1)~=ri
    r=[ri;r];
end
if r(end)~=rf
    r=[r;rf];
end
% rough path done. Now tighten the string:
continflag=1;
iter=0;
while continflag
    iter=iter+1;
    if iter>50000
        continflag=0;
        warning('Max iterations exceeded.')
    end
    rold = r;
    cold = c;
    r2 = [r(1);(r(1:end-2)+r(3:end))/2;r(end)];
    c2 = [c(1);(c(1:end-2)+c(3:end))/2;c(end)];
    dr = r2-r;
    dc = c2-c;
    dn = .5*sqrt(dr.^2+dc.^2);
    k = dn>.1;
    dr(k) = .1*dr(k)./dn(k);
    dc(k) = .1*dc(k)./dn(k);
    r=r+dr;
    c=c+dc;
    k=interpn(M,r,c,'*nearest')>.5;
    r(k)=r(k)-dr(k);
    c(k)=c(k)-dc(k);
    if max(abs([r-rold;c-cold])) < 1e-4 % decrease to 1e-6 for finer precision
        continflag=0;
    end
end
varargout{1}=r;
varargout{2}=c;
