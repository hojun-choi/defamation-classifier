package com.defamation.backend.service;

import com.defamation.backend.repository.CaseRepository;
import com.defamation.backend.web.dto.CaseDto;
import com.defamation.backend.web.dto.PageResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CaseService {

    private final CaseRepository caseRepository;
    private final ObjectMapper om = new ObjectMapper();

    /**
     * 실제 판례 검색/페이지네이션
     */
    public PageResponse<CaseDto> searchCases(String q, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<CaseDto> result = caseRepository.search(q, pageable)
                .map(c -> CaseDto.from(c, om));

        return PageResponse.<CaseDto>builder()
                .items(result.getContent())
                .page(page)
                .size(size)
                .totalElements(result.getTotalElements())
                .totalPages(result.getTotalPages())
                .build();
    }
}
